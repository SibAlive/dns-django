from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import logging

from .models import Cart
from .cart_manager import CartManager


logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """Объединение корзины при входе пользователя"""
    logger.debug(f"=== СИГНАЛ ВХОДА: пользователь {user.username} ===")
    # Получаем secret_key из куки (старый ключ)
    old_session_key = request.COOKIES.get('sessionid')

    if not old_session_key:
        return

    try:
        logger.debug(f"Ищем корзину с session_key={old_session_key}, user__isnull=True")
        # Получаем избранное из сессии
        session_cart = Cart.objects.get(session_key=old_session_key, user__isnull=True)

        # Получаем или создаем корзину пользователя
        user_cart, created = Cart.objects.get_or_create(user=user)

        # Если корзины разные, переносим товар
        if session_cart != user_cart:
            for item in session_cart.items.all():
                cart_item, created = user_cart.items.get_or_create(
                    product=item.product,
                    defaults={
                        'quantity': item.quantity,
                        'price': item.price,
                    }
                )

                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()

        # Удаляем сессионную корзину
        session_cart.delete()

        logger.debug("Сессионное избранное удалено")

    except Cart.DoesNotExist:
        logger.warning(f"Корзина с session_key={old_session_key} не найдена")

