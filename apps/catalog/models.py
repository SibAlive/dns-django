import os

from django.urls import reverse
from django.utils import timezone
from pytils.translit import slugify
from django.core.validators import MinLengthValidator
from django.db import models

from .utils import product_image_path


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Категория',
                            validators=[
                                MinLengthValidator(3, message="Минимум 3 символа")
                            ]
                            )
    slug = models.SlugField(unique=True, db_index=True)
    picture = models.ImageField(upload_to='catalog/category/', default=None,
                                blank=True, verbose_name='Изображение')

    class Meta:
        verbose_name = "Категория" # Меняет заголовок модели в админ панели
        verbose_name_plural = "Категории" # Заголовок для множественного числа

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'cat_slug': self.slug})

    def save(self, *args, **kwargs):
        # Создаем slug если его нет
        if not self.slug:
            self.slug = slugify(self.name)

        # Переименовываем файл изображения
        if self.picture:
            # Получаем расширение файла
            extension = os.path.splitext(self.picture.name)[1]
            # Формируем новое имя файла
            new_filename = f"{self.slug}{extension}"
            # Меняем имя файла
            self.picture.name = new_filename

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name='Подкатегория',
                            validators=[
                                MinLengthValidator(3, message="Минимум 3 символа")
                            ]
                            )
    slug = models.SlugField(unique=True, db_index=True)
    picture = models.ImageField(upload_to='catalog/subcategory/', default=None,
                                blank=True, verbose_name='Изображение')

    cat = models.ForeignKey(Category, on_delete=models.PROTECT,
                            related_name='subcat', verbose_name='Категория')

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def get_absolute_url(self):
        return reverse('catalog:products', kwargs={'subcat_slug': self.slug})

    def save(self, *args, **kwargs):
        # Создаем slug если его нет
        if not self.slug:
            self.slug = slugify(self.name)

        # Переименовываем файл изображения
        if self.picture:
            # Получаем расширение файла
            extension = os.path.splitext(self.picture.name)[1]
            # Формируем новое имя файла
            new_filename = f"{self.slug}{extension}"
            # Меняем имя файла
            self.picture.name = new_filename

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Товар',
                            validators=[
                                MinLengthValidator(5, message="Минимум 5 символов")
                            ]
                            )
    slug = models.SlugField(unique=True, db_index=True, max_length=100)
    description = models.TextField(max_length=500, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Остаток')
    sku = models.PositiveIntegerField(blank=True, null=True, verbose_name='Артикул')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    subcat = models.ForeignKey(SubCategory, on_delete=models.PROTECT,
                               related_name='products', verbose_name='Подкатегория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def get_absolute_url(self):
        return reverse('catalog:product', kwargs={'product_slug': self.slug})

    def save(self, *args, **kwargs):
        # Создаем slug если его нет
        if not self.slug:
            self.slug = slugify(self.name)

        # Если при редактировании товара цена изменилась, сохраняем её в PriceHistory
        # Проверяем, существует ли уже товар
        if self.pk:
            old_product = Product.objects.get(pk=self.pk)
            # Если цена изменилась
            if old_product.price != self.price:
                PriceHistory.objects.create(
                    product=self,
                    price=old_product.price,
                    changed_at=timezone.now()
                )
        super().save(*args, **kwargs)

    @property
    def main_image(self):
        """Возвращает главное фото товара"""
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image
        # Если нет главного фото, возвращаем первое
        first = self.images.first()
        return first.image if first else None

    @property
    def additional_images(self):
        """Возвращает дополнительные фото"""
        return self.images.filter(is_main=False)

    def get_old_price(self):
        """Возвращает предыдущую цену, если она была выше ткущей"""
        try:
            # Получаем последнюю запись из истории цен
            last_price = self.prices.exclude(price=self.price).first()
            if last_price and last_price.price > self.price:
                return last_price.price
            return None
        except:
            return None

    def get_discount_percent(self):
        """Возвращает процент скидки"""
        old_price = self.get_old_price()
        if old_price and old_price > self.price:
            discount = ((old_price - self.price) / old_price) * 100
            return round(discount)
        return 0

    def __str__(self):
        return self.name


class PriceHistory(models.Model):
    """Модель для истории цен товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']


class ProductImage(models.Model):
    """Модель для фотографий товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_path, verbose_name='Изображение',
                              max_length=500)
    is_main = models.BooleanField(default=False, verbose_name='Главное фото')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фотография товара'
        verbose_name_plural = 'Фотографии товара'
        ordering = ['-is_main', 'order', 'created_at']
        # Только одно главное фото на товар
        constraints = [
            models.UniqueConstraint(
                fields=('product', 'is_main'),
                condition=models.Q(is_main=True),
                name='unique_main_image_per_product'
            )
        ]

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем порядковый номер, если не указан
        if self.order == 0 and not self.pk:
            max_order = ProductImage.objects.filter(product=self.product).aggregate(
                models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1

        # Если это главное фото, убираем флаг is_main у остальных фотографий товара
        if self.is_main:
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Фото для {self.product.name} (ID: {self.pk})"

    def delete(self, *args, **kwargs):
        # При удалении фото удаляем и файл
        storage = self.image.storage
        if storage.exists(self.image.name):
            storage.delete(self.image.name)
        super().delete(*args, **kwargs)