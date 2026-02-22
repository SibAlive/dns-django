from datetime import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm


User = get_user_model()


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='E-mail или Логин',
                               widget = forms.TextInput(attrs={'class': 'form-contact'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-contact'}))


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-contact', 'placeholder': 'Введите ваш E-mail'}))
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-contact'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-contact'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-contact'}))

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким E-mail уже существует")
        return email

class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(disabled=True, label='E-mail',
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    this_year = datetime.today().year
    date_birth = forms.DateField(
        widget=forms.SelectDateWidget(years=tuple(range(this_year-70, this_year-5))),
        required=False)

    class Meta:
        model = get_user_model()
        fields = ('photo', 'username', 'email', 'date_birth', 'first_name', 'last_name')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'})
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль',
                                   widget=forms.PasswordInput(attrs={'class': 'form-contact'}))
    new_password1 = forms.CharField(label='Новый пароль',
                                    widget=forms.PasswordInput(attrs={'class': 'form-contact'}))
    new_password2 = forms.CharField(label='Повтор пароля',
                                    widget=forms.PasswordInput(attrs={'class': 'form-contact'}))
