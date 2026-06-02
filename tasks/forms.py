from django import forms
from .models import IceCream


class UserSearchForm(forms.Form):

    user_id = forms.IntegerField(
        label='ID пользователя'
    )


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