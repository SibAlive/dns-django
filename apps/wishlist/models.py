from django.db import models
from django.conf import settings

from apps.catalog.models import Product


class Wishlist(models.Model):
    """Модель списка избранного пользователя"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist',
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
    products = models.ManyToManyField(
        Product,
        related_name='wishlist',
        verbose_name='Товары',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Список избранного'
        unique_together = (('user', 'session_key'), )

    def __str__(self):
        if self.user:
            return f"Избранное пользователя {self.user.username}"
        return f"Избранное (сессия: {self.session_key})"

    def get_items_count(self):
        """Количество товаров в избранном"""
        return self.products.count()

    def get_total_price(self):
        """Вычисляет общую сумму всех товаров в избранном"""
        return sum(product.price for product in self.products.all())