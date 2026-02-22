from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    max_num = None
    verbose_name = 'Товар в корзине'
    verbose_name_plural = 'Товары в корзине'

    fields = ('product', 'quantity', 'price', 'get_cost', 'product_link')
    readonly_fields = ('get_cost', 'product_link', 'created_at', 'updated_at')
    ordering = ('-created_at', )
    autocomplete_fields = ('product', )

    def get_cost(self, obj):
        """Отформатированная стоимость позиции"""
        return f'{obj.get_cost():.2f} ₽'
    get_cost.short_description = 'Стоимость'

    def product_link(self, obj):
        """Ссылка на товар"""
        if obj.product:
            url = reverse('admin:catalog_product_change', args=[obj.product.id])
            return format_html(f'<a href="{url}">{obj.product.name}</a>')
    product_link.short_description = 'Ссылка на товар'

    def has_add_permission(self, request, obj=None):
        """Разрешаем добавление товаров в корзину через админку"""
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product', 'cart__user')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    # Поля для детального просмотра
    fieldsets = (
        ('Информация о владельце', {
            'fields': ('user', 'session_key')
        }),
        ('Статистика корзины', {
            'fields': ('get_items_count', 'get_total_price_formatted', 'get_total_quantity')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Поля для списка
    list_display = (
        'id',
        'user_info',
        'session_key_short',
        'get_items_count',
        'get_total_price_formatted',
        'get_total_quantity',
        'updated_at'
    )

    # Фильтры
    list_filter = ('created_at', 'updated_at', 'user__is_staff')

    # Поиск
    search_fields = ('user__username', 'user__email')

    # Поля только для чтения
    readonly_fields = (
        'created_at',
        'updated_at',
        'get_items_count',
        'get_total_price_formatted',
        'get_total_quantity'
    )
    list_display_links = ('user_info', )

    inlines = [CartItemInline]

    list_per_page = 25
    list_select_related = ('user',)
    date_hierarchy = 'created_at'

    def user_info(self, obj):
        """Информация о пользователе"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small style="color: #666;">{}</small>',
                obj.user.username,
                obj.user.email or 'нет email'
            )
        return format_html('<span style="color: #999;">Анонимный пользователь</span>')

    user_info.short_description = 'Пользователь'
    user_info.admin_order_field = 'user__username'

    def session_key_short(self, obj):
        """Сокращенный ключ сессии"""
        if obj.session_key:
            return f'{obj.session_key[:8]}...'
        return '-'

    session_key_short.short_description = 'Сессия'

    def get_items_count(self, obj):
        """Количество уникальных товаров"""
        count = obj.items.count()
        return format_html('<b>{}</b>', count)

    get_items_count.short_description = 'Кол-во позиций'

    def get_total_quantity(self, obj):
        """Общее количество товаров"""
        total = obj.get_total_quantity()
        return format_html('<b>{} шт.</b>', total)
    get_total_quantity.short_description = 'Всего товаров'

    def get_total_price_formatted(self, obj):
        """Форматированная общая стоимость"""
        total = obj.get_total_price()
        return format_html(
            '<span style="color: green; font-weight: bold;">{} ₽</span>',
            f'{total:.2f}'  # Форматируем число отдельно
        )
    get_total_price_formatted.short_description = 'Общая стоимость'

    # Действия над корзинами
    actions = ['clear_selected_carts']

    def clear_selected_carts(self, request, queryset):
        """Очистить выбранные корзины"""
        for cart in queryset:
            cart.clear()
        self.message_user(request, f'Очищено {queryset.count()} корзин')
    clear_selected_carts.short_description = 'Очистить выбранные корзины'

    # Переопределяем queryset для оптимизации
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('items', 'items__product')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cart_link',
        'product_info',
        'quantity',
        'price',
        'get_cost',
        'updated_at'
    )
    list_filter = ('created_at', 'cart__user')
    search_fields = (
        'product__name',
        'cart__user__username',
        'cart__session_key'
    )
    readonly_fields = ('get_cost', 'created_at', 'updated_at')
    raw_id_fields = ('cart', 'product')
    list_select_related = ('cart__user', 'product')

    fieldsets = (
        ('Основная информация', {
            'fields': ('cart', 'product')
        }),
        ('Количество и цена', {
            'fields': ('quantity', 'price', 'get_cost')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def cart_link(self, obj):
        """Ссылка на корзину"""
        url = reverse('admin:cart_cart_change', args=[obj.cart.id])
        if obj.cart.user:
            return format_html('<a href="{}">Корзина {}</a>', url, obj.cart.user.username)
        return format_html('<a href="{}">Корзина #{}</a>', url, obj.cart.id)

    cart_link.short_description = 'Корзина'

    def product_info(self, obj):
        """Информация о товаре"""
        return format_html(
            '<strong>{}</strong><br><small>Арт: {}</small>',
            obj.product.name,
            obj.product.article if hasattr(obj.product, 'article') else '—'
        )

    product_info.short_description = 'Товар'

    def get_cost(self, obj):
        """Стоимость позиции"""
        return f'{obj.get_cost():.2f} ₽'

    get_cost.short_description = 'Стоимость'

    # Действия
    actions = ['duplicate_item', 'update_prices']

    def duplicate_item(self, request, queryset):
        """Дублировать выбранные позиции"""
        for item in queryset:
            item.pk = None
            item.quantity = 1
            item.save()
        self.message_user(request, f'Создано дубликатов: {queryset.count()}')

    duplicate_item.short_description = 'Дублировать позиции'

    def update_prices(self, request, queryset):
        """Обновить цены до актуальных"""
        updated = 0
        for item in queryset:
            if item.price != item.product.price:
                item.price = item.product.price
                item.save()
                updated += 1
        self.message_user(request, f'Обновлено цен: {updated}')

    update_prices.short_description = 'Обновить цены'