from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email",)

# Help-Blog
# https://wsvincent.com/django-allauth-tutorial-custom-user-model/#:~:text=A%20custom%20user%20model%20is,add%20social%20auth%20as%20needed


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (UserChangeForm.Meta.fields)
