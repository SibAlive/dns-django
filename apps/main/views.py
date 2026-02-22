from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'main/index.html'
    extra_context = {
        'title': 'Главная страница'
    }