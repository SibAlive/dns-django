from django.db.models import QuerySet


class SortableListViewMixin:
    """Миксин для добавления сортировки в ListView"""
    sort_fields = ('name', 'price', 'created_at')
    default_sort = 'name'
    default_direction = 'asc'

    def get_sort_params(self):
        """Получаем параметры сортировки из запроса"""
        sort_by = self.request.GET.get('sort', self.default_sort)
        direction = self.request.GET.get('direction', self.default_direction)

        if sort_by not in self.sort_fields:
            sort_by = self.default_sort

        if direction not in ('asc', 'desc'):
            direction = self.default_direction

        return sort_by, direction

    def get_ordering(self):
        """Возвращает поле для сортировки"""
        sort_by, direction = self.get_sort_params()
        return f'-{sort_by}' if direction == 'desc' else sort_by

    def get_queryset(self):
        """Применяем сортировку"""
        queryset = super().get_queryset()
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort_by, direction = self.get_sort_params()
        context['current_sort'] = sort_by
        context['current_direction'] = direction
        return context