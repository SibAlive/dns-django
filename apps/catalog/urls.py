from django.urls import path, reverse_lazy

from . import views


app_name = 'catalog'

urlpatterns = [
    path('', views.ShowCategories.as_view(), name='categories'),
    path('category/<slug:cat_slug>/', views.ShowCategory.as_view(), name='category'),
    path('products/<slug:subcat_slug>/', views.ShowProducts.as_view(), name='products'),
    path('product/<slug:product_slug>/', views.ShowProduct.as_view(), name='product'),

]