from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользовательская модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='E-mail')
    photo = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Фотография')
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', )

    class Meta:
        db_table = 'users_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email