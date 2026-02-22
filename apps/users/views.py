from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from dns_django import settings
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm


class LoginUser(LoginView):
    """Класс входа пользователя"""
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class RegisterUser(CreateView):
    """Класс регистрации пользователя"""
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')


class ProfileView(LoginRequiredMixin, DetailView):
    """Класс для просмотра профиля"""
    model = get_user_model()
    template_name = 'users/profile_detail.html'
    context_object_name = 'user'
    extra_context = {
        'title': 'Мой профиль',
        'default_image': settings.DEFAULT_USER_IMAGE
    }
    def get_object(self, queryset=None):
        """Метод определяет какой именно объект нужно редактировать.
        В данном случае пользователь редактирует только свой профиль"""
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Класс для редактирования профиля"""
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile_edit.html'
    extra_context = {
        'title': 'Мой профиль',
        'default_image': settings.DEFAULT_USER_IMAGE
    }

    def get_success_url(self):
        return reverse_lazy('users:profile_detail')

    def get_object(self, queryset=None):
        """Метод определяет какой именно объект нужно редактировать.
        В данном случае пользователь редактирует только свой профиль"""
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = "users/password_change_form.html"