from django.contrib import admin
from django.utils.html import format_html

from .models import Category, SubCategory, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5
    fields = ('image', 'is_main', 'order', 'image_preview')
    readonly_fields = ('image_preview', )
    ordering = ('order', )

    def image_preview(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "нет фото"
    image_preview.short_description = 'Превью'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'picture') # Поля, отображаемые в форме редактирования
    readonly_fields = ('slug', ) # Делает поля не редактируемыми
    # prepopulated_fields = {'slug': ('name',)} # Предзаполняет поле на основе других полей
    list_display = ('name', 'slug', 'picture_preview') # Отображаемые поля

    def picture_preview(self, obj):
        if obj.picture:
            return format_html(f'<img src="{obj.picture.url}" width="50" height="50" />')
        return "Нет изображения"
    picture_preview.short_description = 'Изображение'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'cat', 'picture')
    readonly_fields = ('slug', )
    list_display = ('name', 'slug', 'cat', 'picture_preview')
    list_filter = ('cat', ) # Фильтрация

    def picture_preview(self, obj):
        if obj.picture:
            return format_html(f'<img src="{obj.picture.url}" width="50" height="50" />')
        return "Нет изображения"
    picture_preview.short_description = 'Изображение'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'subcat', 'price', 'description', 'stock_quantity', 'sku')
    readonly_fields = ('slug',)
    list_display = ('name', 'slug', 'price', 'description', 'stock_quantity',
                    'subcat', 'sku', 'main_image_preview')
    list_filter = ('subcat__cat', 'subcat')
    search_fields = ('name', 'description')
    inlines = (ProductImageInline, )

    def main_image_preview(self, obj):
        main_img = obj.main_image
        if main_img:
            return format_html(f'<img src="{main_img.url}" width="50" height="50" />')
        return "Нет фото"
    main_image_preview.short_description = 'Главное фото'

    def images_count(self, obj):
        """Метод для отображения количества фото"""
        return obj.images.count()
    images_count.short_description = 'Кол-во фото'