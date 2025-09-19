from django import forms
from django.contrib.auth.models import User


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]  # только имя
        labels = {
            "username": "Имя пользователя",
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите новое имя"
            })
        }


