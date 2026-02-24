document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - cart.js initialized');

    // Функция для показа уведомления
    function showNotification(message, type = 'success') {
        const container = document.getElementById('messages-container');
        if (!container) {
            console.error('Messages container not found');
            return;
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);

        const closeBtn = alertDiv.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 300);
            });
        }
    }

    // Функция для обновления количества конкретного товара
    function updateProductQuantity(productId, newQuantity) {
        const productCard = document.querySelector(`.cart-card[data-product-id="${productId}"]`);
        if (productCard) {
            const quantityElement = productCard.querySelector('.cart-prod-qty');
            if (quantityElement) {
                quantityElement.textContent = `× ${newQuantity} шт.`;
            }
        }
    }

    // Функция для обновления UI корзины (итоги)
    function updateCartUI(cartData) {
        console.log('Updating cart UI with data:', cartData);

        const totalPriceElement = document.getElementById('total-price');
        const totalQuantityElement = document.getElementById('total-quantity');

        if (totalPriceElement) {
            const price = parseFloat(cartData.total_price);
            totalPriceElement.textContent = price.toLocaleString('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }) + ' ₽';
        }
        if (totalQuantityElement) {
            totalQuantityElement.textContent = cartData.total_quantity;
        }
    }

    // --- ОБРАБОТКА ДОБАВЛЕНИЯ ТОВАРА ---
    const addForms = document.querySelectorAll('.add-to-cart-form');
    console.log('Found add forms:', addForms.length);

    addForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Add form submitted');

            const formData = new FormData(this);
            const url = this.action;
            const productId = this.closest('.cart-card').dataset.productId;

            const button = this.querySelector('button');
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = 'Добавление...';

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    },
                    body: formData
                });

                const data = await response.json();
                console.log('Response data:', data);

                if (data.success) {
                    showNotification(data.message, 'success');
                    if (data.cart) {
                        updateCartUI(data.cart);
                        const currentQuantityElement = this.closest('.cart-card').querySelector('.cart-prod-qty');
                        const currentQuantity = parseInt(currentQuantityElement.textContent.replace(/[^0-9]/g, ''));
                        updateProductQuantity(productId, currentQuantity + 1);
                    }
                } else {
                    showNotification(data.message || 'Произошла ошибка', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Ошибка при отправке запроса', 'error');
            } finally {
                button.disabled = false;
                button.textContent = originalText;
            }
        });
    });

    // --- ОБРАБОТКА УДАЛЕНИЯ ТОВАРА (ИСПРАВЛЕНО) ---
    const removeForms = document.querySelectorAll('.remove-from-cart-form');
    console.log('Found remove forms:', removeForms.length);

    removeForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Remove form submitted');

            const formData = new FormData(this);
            const cartCard = this.closest('.cart-card');
            const url = this.action;

            const button = this.querySelector('button');
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = 'Удаление...';

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }

                const data = await response.json();
                console.log('Response data:', data);

                if (data.success) {
                    showNotification(data.message || 'Товар удален из корзины', 'success');

                    if (data.cart) {
                        updateCartUI(data.cart);
                    }

                    // Логика обновления карточки
                    const currentQuantityElement = cartCard.querySelector('.cart-prod-qty');
                    const currentText = currentQuantityElement ? currentQuantityElement.textContent : "× 1 шт.";
                    const currentQty = parseInt(currentText.replace(/[^0-9]/g, '')) || 1;
                    const newQty = currentQty - 1;

                    if (newQty <= 0) {
                        // Удаляем карточку полностью
                        cartCard.remove();

                        // Проверка на пустую корзину
                        const remainingCards = document.querySelectorAll('.cart-card').length;
                        if (remainingCards === 0) {
                            const cartContent = document.getElementById('cart-content');
                            if (cartContent) {
                                // ВНИМАНИЕ: URL '/catalog/' нужно заменить на ваш реальный путь,
                                // так как {% url %} не работает в .js файлах.
                                cartContent.innerHTML = `
                                    <div id="empty-cart-message" class="cart-empty">Ваша корзина пуста</div>
                                    <div class="cart-bottom-actions">
                                        <a href="/catalog/" class="cart-bottom-btn">Перейти в каталог</a>
                                    </div>
                                `;
                            }
                        }
                    } else {
                        // Обновляем только количество
                        if (currentQuantityElement) {
                            currentQuantityElement.textContent = `× ${newQty} шт.`;
                        }
                        // Анимация
                        cartCard.style.transition = "opacity 0.3s";
                        cartCard.style.opacity = "0.5";
                        setTimeout(() => cartCard.style.opacity = "1", 300);
                    }
                } else {
                    showNotification(data.message || 'Произошла ошибка', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Ошибка: ' + error.message, 'error');
            } finally {
                if (button) {
                    button.disabled = false;
                    button.textContent = originalText;
                }
            }
        });
    });

    // --- ОБРАБОТКА ОЧИСТКИ КОРЗИНЫ ---
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        console.log('Clear cart button found');

        clearCartBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('Clear cart clicked');

            // Ищем токен в любой форме на странице или в meta-теге
            let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            // Если не нашли в форме, пробуем найти в meta-теге (стандартная практика Django)
            if (!csrfToken) {
                csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                            document.querySelector('[data-csrf]')?.dataset.csrf ||
                            document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
            }

            if (!csrfToken) {
                showNotification('Ошибка CSRF-токена', 'error');
                return;
            }

            const originalText = this.textContent;
            this.textContent = 'Очистка...';
            this.style.pointerEvents = 'none';

            try {
                const response = await fetch(this.href, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                });

                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }

                const data = await response.json();
                console.log('Response data:', data);

                if (data.success) {
                    showNotification('Корзина очищена', 'success');

                    const cartContent = document.getElementById('cart-content');
                    if (cartContent) {
                        // Замените /catalog/ на ваш реальный URL категорий
                        cartContent.innerHTML = `
                            <div id="empty-cart-message" class="cart-empty">Ваша корзина пуста</div>
                            <div class="cart-bottom-actions">
                                <a href="/catalog/" class="cart-bottom-btn">Перейти в каталог</a>
                            </div>
                        `;
                    }
                } else {
                    showNotification(data.message || 'Ошибка при очистке', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Ошибка: ' + error.message, 'error');
            } finally {
                this.textContent = originalText;
                this.style.pointerEvents = 'auto';
            }
        });
    }

    // Отладка
    console.log('Cart cards found:', document.querySelectorAll('.cart-card').length);
    console.log('Total price element:', document.getElementById('total-price'));
    console.log('Total quantity element:', document.getElementById('total-quantity'));
});