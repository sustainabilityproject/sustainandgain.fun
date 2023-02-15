from django.urls import path
from accounts.views import RegisterView, profile
import os

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", profile ,name="profile"),
]


