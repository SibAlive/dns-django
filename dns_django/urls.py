from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from dns_django import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.main.urls')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('catalog/', include('apps.catalog.urls', namespace='catalog')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('wishlist/', include('apps.wishlist.urls', namespace='wishlist')),
]

# Необходимо для отображения файлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)