from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BuiltinUserAdmin
from accounts.forms import UserCreationForm, UserChangeForm
from accounts.models import User
from . models import Profile


class UserAdmin(BuiltinUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ["username", "email", ]


admin.site.register(User, UserAdmin)
admin.site.register(Profile)