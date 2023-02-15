from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BuiltinUserAdmin
from . models import Profile
from accounts.forms import UserCreationForm, UserChangeForm
from accounts.models import User


class UserAdmin(BuiltinUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ["username", "email", ]


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
