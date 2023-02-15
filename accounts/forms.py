from django import forms
from django.contrib.auth.forms import UserCreationForm as BuiltinUserCreationForm
from django.contrib.auth.forms import UserChangeForm as BuiltinUserChangeForm

from accounts.models import User


class UserCreationForm(BuiltinUserCreationForm):
    email = forms.EmailField(required=True, help_text="Required.")

    class Meta:
        model = User
        fields = ("username", "email")


class UserChangeForm(BuiltinUserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email")
