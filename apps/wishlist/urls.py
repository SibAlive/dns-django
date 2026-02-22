from django.urls import path

from . import views


app_name = 'wishlist'


urlpatterns = [
    path('', views.wishlist_detail, name='detail'),
    path('add/<int:product_id>/', views.wishlist_add, name='add'),
    path('clear/', views.wishlist_clear, name='clear')
]