document.addEventListener('DOMContentLoaded', function() {
    // Функция для получения CSRF токена из cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Обработка кнопок избранного
    document.querySelectorAll('.favorite-toggle-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();

            const url = this.dataset.url;
            const productId = this.dataset.productId;
            const btnElement = this; // Сохраняем ссылку на кнопку

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.added) {
                    btnElement.classList.add('is-fav');
                } else {
                    btnElement.classList.remove('is-fav');
                }

                // Обновляем счетчик избранного в шапке, если он есть
                const favCounter = document.querySelector('.favorites-count');
                if (favCounter && data.wishlist_count !== undefined) {
                    favCounter.textContent = data.wishlist_count;
                }

                // Если мы на странице избранного, удаляем карточку товара
                if (window.location.pathname.includes('wishlist') ||
                    window.location.pathname.includes('favorites')) {

                    // Находим и удаляем карточку текущего товара
                    const productCard = btnElement.closest('.cart-card-dns');
                    if (productCard) {
                        // Анимация удаления
                        productCard.style.transition = 'opacity 0.3s';
                        productCard.style.opacity = '0';

                        setTimeout(() => {
                            productCard.remove();

                            // Проверяем, остались ли товары в избранном
                            const remainingCards = document.querySelectorAll('.cart-card-dns');
                            const orderSummary = document.querySelector('.order-summary-dns');

                            if (remainingCards.length === 0) {
                                // Если товаров нет, показываем сообщение
                                if (orderSummary) {
                                    orderSummary.innerHTML = '<div class="order-count">В избранном пока нет товаров</div>';
                                }
                            } else {
                                // Обновляем сумму и количество товаров
                                updateWishlistSummary();
                            }
                        }, 300);
                    }
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });

    // Функция для обновления суммы и количества товаров в избранном
    function updateWishlistSummary() {
        const orderSummary = document.querySelector('.order-summary-dns');
        if (!orderSummary) return;

        const productCards = document.querySelectorAll('.cart-card-dns');
        const totalCount = productCards.length;

        let totalSum = 0;
        productCards.forEach(card => {
            const priceElement = card.querySelector('.cart-price-dns');
            if (priceElement) {
                // Извлекаем число из строки (убираем "₽" и пробелы)
                const priceText = priceElement.textContent.replace('₽', '').replace(/\s/g, '').trim();
                const price = parseFloat(priceText);
                if (!isNaN(price)) {
                    totalSum += price;
                }
            }
        });

        // Форматируем сумму с пробелами
        const formattedSum = totalSum.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");

        // Обновляем текст
        const orderCountElement = orderSummary.querySelector('.order-count');
        if (orderCountElement) {
            orderCountElement.innerHTML = `Товаров: ${totalCount}, на сумму <span class="order-total">${formattedSum} ₽</span>`;
        }
    }
});