from .models import Wishlist


def wishlist_products(request):
    """Добавляет список ID товаров в избранном в контекст шаблона"""
    wishlist_products = []

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
    else:
        if request.session.session_key:
            session_key = request.session.session_key
            wishlist = Wishlist.objects.filter(session_key=session_key).first()
        else:
            wishlist = None

    if wishlist:
        wishlist_products = wishlist.products.values_list('id', flat=True)

    return {
        'wishlist_products': list(wishlist_products)
    }