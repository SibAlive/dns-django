from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem


class CartManager:
    """Менеджер для работы с корзиной"""
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self.session_key = request.session.session_key

        # Создаем сессию если её нет
        if not self.session_key:
            self.request.session.save()
            self.session_key = self.request.session.session_key

        self.cart = self._get_cart()

    def _get_cart(self):
        """Получить корзину для пользователя или сессии"""
        # Для авторизованного пользователя
        if self.user and self.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.user)
            return cart

        # Для неавторизованного пользователя - по сессии
        cart, created = Cart.objects.get_or_create(session_key=self.session_key)
        return cart

    def _merge_session_cart(self, user_cart):
        """Переносит товары из сессионной корзины в корзину пользователя"""
        try:
            session_cart = Cart.objects.get(session_key=self.session_key)

            if session_cart and session_cart != user_cart:
                with transaction.atomic():
                    for item in session_cart.items.all():
                        self._add_item(
                            user_cart,
                            item.product,
                            item.quantity,
                            save=False
                        )
                    # Деактивируем сессионную корзину
                    session_cart.is_active = False
                    session_cart.save()

        except Cart.DoesNotExist:
            pass

    @staticmethod
    def _add_item(cart, product, quantity=1):
        """Добавляет товар в корзину (внутренний метод)"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.price
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    @staticmethod
    def _remove_item(cart, product, quantity=1):
        """Удаляет товар из корзины (внутренний метод)"""
        cart_item = CartItem.objects.get(cart=cart, product=product)

        cart_item.quantity -= quantity

        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()

    def add(self, product, quantity=1):
        """Публичный метод добавление товара в корзину"""
        if quantity < 1:
            raise ValueError("Количество должно быть положительным")

        return self._add_item(self.cart, product, quantity)

    def remove(self, product):
        """Удалить товар из корзины"""
        self._remove_item(self.cart, product)

    def update_quantity(self, product, quantity):
        """Уменьшить количество товара в корзине"""
        if quantity < 1:
            self.remove(product)
            return

        cart_item = get_object_or_404(
            CartItem,
            cart=self.cart,
            product=product
        )
        cart_item.quantity = quantity
        cart_item.save()

    def clear(self):
        """Очистить корзину"""
        self.cart.items.all().delete()

    def get_items(self):
        """Возвращает все товары в корзине"""
        return self.cart.items.select_related('product').all()

    def get_total_price(self):
        """Получить общую стоимость"""
        total = Decimal(0)
        for item in self.get_items():
            total += item.price * item.quantity
        return total

    def get_total_quantity(self):
        """Возвращает общее количество товаров"""
        total = 0
        for item in self.get_items():
            total += item.quantity
        return total

    def count_items(self):
        """Возвращает количество позиций"""
        return self.cart.items.count()

    def is_empty(self):
        """Проверяет, пустая ли корзина"""
        return not self.cart.items.exists()