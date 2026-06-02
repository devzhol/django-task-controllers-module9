from django import forms


class FeedbackForm(forms.Form):

    # Имя пользователя
    name = forms.CharField(
        max_length=100,
        label='Имя'
    )

    # Email
    email = forms.EmailField(
        label='Email'
    )

    # Сообщение
    message = forms.CharField(
        widget=forms.Textarea,
        label='Сообщение'
    )