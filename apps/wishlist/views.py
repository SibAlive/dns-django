from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import Wishlist, Product
from dns_django import settings


def get_wishlist(request):
    """Получение или создание избранного для текущего пользователя/сессии"""
    if request.user.is_authenticated:
        # Для авторизованных - по пользователю
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user
        )
        if created:
            wishlist.session_key = None
            wishlist.save()
    else:
        # Для неавторизованных - по сессии
        if not request.session.session_key:
            request.session.save() # Создаем сессию, если её нет

        session_key = request.session.session_key
        wishlist, created = Wishlist.objects.get_or_create(
            session_key=session_key,
        )
        if created:
            wishlist.user = None
            wishlist.save()

    return wishlist

def wishlist_detail(request):
    """Просмотр избранного"""
    wishlist = get_wishlist(request)

    return render(request, 'wishlist/wishlist_detail.html',
                  context = {
                      'wishlist': wishlist,
                      'default_image': settings.DEFAULT_PRODUCT_IMAGE,
                  })


@require_POST
def wishlist_add(request, product_id):
    """Добавление/удаления товара из избранного"""
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_wishlist(request)

    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        added = False
        message = f'Товар "{product.name}" удален из избранного'
    else:
        wishlist.products.add(product)
        added = True
        message = f'Товар "{product.name}" добавлен в избранное'

    # Проверяем, AJAX ли запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'added' : added,
            'product_id': product.id,
            'message': message,
            'wishlist_count': wishlist.products.count()
        })
    else:
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'product_detail'))


def wishlist_clear(request):
    """Очистка избранного"""
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist.products.clear()
    messages.success(request, 'Список избранного очищен')
    return redirect('wishlist:detail')


