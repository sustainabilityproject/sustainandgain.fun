from accounts.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

def profile(request):
    return render(request, 'account/profile.html')