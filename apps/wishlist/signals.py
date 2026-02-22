from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import logging

from .models import Wishlist


logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def merge_wishlist_on_login(sender, request, user, **kwargs):
    """Объединение избранного при входе пользователя"""
    logger.debug(f"=== СИГНАЛ ВХОДА: пользователь {user.username} ===")
    # Получаем secret_key из куки (старый ключ)
    old_session_key = request.COOKIES.get('sessionid')

    if not old_session_key:
        return

    try:
        logger.debug(f"Ищем избранное с session_key={old_session_key}, user__isnull=True")
        # Получаем избранное из сессии
        session_wishlist = Wishlist.objects.get(session_key=old_session_key, user__isnull=True)
        logger.info(f"Найдено избранное в сессии с {session_wishlist.products.count()} товарами")

        # Получаем или создаем избранное пользователя
        user_wishlist, created = Wishlist.objects.get_or_create(user=user)

        # Добавляем товары из сессии в избранное пользователя
        for product in session_wishlist.products.all():
            if not user_wishlist.products.filter(id=product.id).exists():
                user_wishlist.products.add(product)
            else:
                logger.info(f"Товар уже есть в избранном: {product.name}")

        # Удаляем временное избранное
        session_wishlist.delete()
        logger.debug("Сессионное избранное удалено")

    except Wishlist.DoesNotExist:
        logger.warning(f"Избранное с session_key={old_session_key} не найдено")