from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.cart.cart_manager import CartManager
from ..catalog.models import Product


def cart_detail(request):
    """Страница корзины"""
    cart_manager = CartManager(request)

    # # Для AJAX-запросов
    # if request.header.get('x-requested-with') == 'XMLHttpRequest':
    #     return JsonResponse(cart_manager.to_dict)

    return render(request, 'cart/cart_detail.html',
                  context={
                      'cart_manager': cart_manager
                  })


@require_POST
def cart_add(request, product_id):
    """Добавление товара в корзину"""
    cart_manager = CartManager(request)
    product = get_object_or_404(Product, pk=product_id)

    quantity = int(request.POST.get('quantity', '1'))

    try:
        cart_manager.add(product, quantity)
        message = f'Товар "{product.name}" добавлен в корзину'

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'cart':{
                    'total_price': str(cart_manager.get_total_price()),
                    'total_quantity': cart_manager.get_total_quantity(),
                    'items_count': cart_manager.count_items()
                }
            })

        messages.success(request, message)

    except ValueError as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

        messages.error(request, str(e))

    return redirect(request.META.get('HTTP_REFERER', 'cart:detail'))


def cart_remove(request, product_id):
    """Удаление товара из корзины"""
    cart_manager = CartManager(request)
    product = get_object_or_404(Product, pk=product_id)

    cart_manager.remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart': {
                'total_price': str(cart_manager.get_total_price()),
                'total_quantity': cart_manager.get_total_quantity(),
                'items_count': cart_manager.count_items()
            }
        })

    messages.success(request, 'Товар удален из корзины')
    return redirect('cart:detail')


def cart_clear(request):
    """Очистка корзины"""
    cart_manager = CartManager(request)
    cart_manager.clear()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart': {
                'total_price': 0,
                'total_quantity': 0,
                'items_count': 0
            }
        })

    messages.success(request, 'Корзина очищена')
    return redirect('cart:detail')