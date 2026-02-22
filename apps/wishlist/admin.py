from django.contrib import admin

from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_items_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('products', )

    def get_items_count(self, obj):
        return obj.products.count()
    get_items_count.short_description = 'Количество товаров'