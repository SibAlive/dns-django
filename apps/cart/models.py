from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.catalog.models import Product


class Cart(models.Model):
    """Модель корзины пользователя"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        verbose_name='Ключ сессии',
        null=True,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = (('user', 'session_key'), )

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username}'
        return f'Корзина (сессия: {self.session_key})'

    def get_total_price(self):
        """Возвращает общую стоимость корзины"""
        return sum(item.get_cost() for item in self.items.all())

    def get_total_quantity(self):
        """Возвращает общее количество товаров"""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Очистить корзину"""
        self.items.all().delete()


class CartItem(models.Model):
    """Модель товара в корзине"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена на момент добавления'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_cost(self):
        """Возвращает стоимость позиции"""
        if self.price is None:
            # Если цена не установлена, используем цену товара
            if self.product and self.product.price:
                return self.product.price * self.quantity
            return 0
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """Сохраняет актуальную цену товара при добавлении"""
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)