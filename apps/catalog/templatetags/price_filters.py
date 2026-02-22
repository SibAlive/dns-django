from django import template


register = template.Library()


@register.filter
def format_price(value):
    """Форматирует цену с пробелами между разрядами"""
    try:
        value = float(value)
        formatted = f"{value:,.0f}".replace(',', ' ')
        return formatted
    except (ValueError, TypeError):
        return value