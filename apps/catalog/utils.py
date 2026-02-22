import os
from django.urls import reverse


def product_image_path(instance, filename):
    """Функция формирует путь для сохранения изображения товара"""
    # Получаем расширение файла
    extension = os.path.splitext(filename)[1]
    # Формируем новое имя файла
    new_filename = f"{instance.product.slug}{extension}"

    # Формируем путь с учетом категории и подкатегории
    cat_slug = instance.product.subcat.cat.slug
    subcat_slug = instance.product.subcat.slug
    product_slug = instance.product.slug

    path = f"catalog/products/{cat_slug}/{subcat_slug}/{product_slug}/{new_filename}"
    return path


def get_breadcrumbs(request, view_name, obj=None):
    """Функция для составления хлебных крошек"""
    breadcrumbs = []

    # Главная страница
    breadcrumbs.append({
        'name': 'Главная',
        'url': reverse('home')
    })

    # Каталог
    breadcrumbs.append({
        'name': 'Каталог',
        'url': reverse('catalog:categories')
    })

    if view_name == 'catalog:category' and obj:
        breadcrumbs.append({
            'name': obj.name,
            'url': obj.get_absolute_url()
        })
    elif view_name == 'catalog:products' and obj:
        breadcrumbs.append({
            'name': obj.cat.name,
            'url': obj.cat.get_absolute_url()
        })
        breadcrumbs.append({
            'name': obj.name,
            'url': obj.get_absolute_url()
        })
    elif view_name == 'catalog:product' and obj:
        breadcrumbs.append({
            'name': obj.subcat.cat.name,
            'url': obj.subcat.cat.get_absolute_url()
        })
        breadcrumbs.append({
            'name': obj.subcat.name,
            'url': obj.subcat.get_absolute_url()
        })
        breadcrumbs.append({
            'name': obj.name,
            'url': obj.get_absolute_url()
        })

    return breadcrumbs