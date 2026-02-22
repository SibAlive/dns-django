from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from dns_django import settings
from .models import Category, SubCategory, Product
from .utils import get_breadcrumbs
from .mixins import SortableListViewMixin


class ShowCategories(ListView):
    """Класс представление формирует список категорий"""
    model = Category
    template_name = 'catalog/categories.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Категории'
        context['breadcrumbs'] = get_breadcrumbs(self.request, 'catalog:categories')
        return context


class ShowCategory(DetailView):
    """Класс представление формирует карточку категории (список подкатегорий)"""
    model = Category
    template_name = 'catalog/category.html'
    slug_url_kwarg = 'cat_slug' # Переменная, которая передается в url

    # def get_object(self, queryset=None):
    #     return get_object_or_404(Category, slug=self.kwargs[self.slug_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        context['category'] = self.object.subcat.all()
        context['breadcrumbs'] = get_breadcrumbs(self.request, 'catalog:category',
                                                 self.object)
        return context


class ShowProducts(SortableListViewMixin, ListView):
    """Класс представление формирует список товаров"""
    model = Product
    template_name = 'catalog/products.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        # Возвращает товары выбранной подкатегории
        queryset = queryset.filter(subcat__slug=self.kwargs.get('subcat_slug'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем наименование подкатегории
        subcategory_slug = self.kwargs.get('subcat_slug')
        subcategory = SubCategory.objects.get(slug=subcategory_slug)

        context['title'] = subcategory
        context['default_image'] = settings.DEFAULT_PRODUCT_IMAGE
        context['breadcrumbs'] = get_breadcrumbs(self.request, 'catalog:products',
                                                 subcategory)
        return context


class ShowProduct(DetailView):
    """Класс представление формирует карточку продукта"""
    model = Product
    template_name = 'catalog/product.html'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image'] = settings.DEFAULT_PRODUCT_IMAGE
        context['breadcrumbs'] = get_breadcrumbs(self.request, 'catalog:product',
                                                 self.object)
        return context