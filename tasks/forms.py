from captcha.fields import CaptchaField
from django import forms
from .models import IceCream


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