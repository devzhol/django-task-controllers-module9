from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import IceCream, UserProfile, Document


class UserSearchForm(forms.Form):

    user_id = forms.IntegerField(
        label='ID пользователя'
    )


class ContactForm(forms.Form):

    name = forms.CharField(max_length=100, label='Имя')
    email = forms.EmailField(label='Email')
    subject = forms.CharField(max_length=150, label='Тема')
    message = forms.CharField(widget=forms.Textarea, label='Сообщение')
    captcha = CaptchaField(label='Проверка')


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['state', 'postal_code', 'iban']
        labels = {
            'state': 'Штат',
            'postal_code': 'Почтовый индекс',
            'iban': 'IBAN',
        }


class IceCreamForm(forms.ModelForm):

    class Meta:
        model = IceCream
        fields = ['name', 'flavor', 'price']
        labels = {
            'name': 'Название',
            'flavor': 'Вкус',
            'price': 'Цена',
        }
        help_texts = {
            'price': 'Укажите цену в формате 0.00',
        }


class DocumentUploadForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ['title', 'description', 'file']
        labels = {
            'title': 'Название документа',
            'description': 'Описание',
            'file': 'Выберите файл (PDF или XLSX)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название документа'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Введите описание (опционально)'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.xlsx'}),
        }


# ============ Authentication Forms ============

class UserLoginForm(forms.Form):
    """Форма входа пользователя"""
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Запомнить меня',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserRegistrationForm(forms.ModelForm):
    """Форма регистрации нового пользователя"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Пароли не совпадают!')
        
        if password and len(password) < 8:
            raise ValidationError('Пароль должен быть не менее 8 символов!')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован!')
        return email


class CustomPasswordResetForm(forms.Form):
    """Форма для восстановления пароля"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email, связанный с вашим аккаунтом',
            'autofocus': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email не найден.')
        return email


class CustomSetPasswordForm(forms.Form):
    """Форма для установки нового пароля"""
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
            'autofocus': True
        }),
        min_length=8
    )
    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите новый пароль'
        }),
        min_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Пароли не совпадают!')
            if len(password1) < 8:
                raise ValidationError('Пароль должен быть не менее 8 символов!')

        return cleaned_data