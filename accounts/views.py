from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import UserCreationForm


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        messages.success(self.request, 'Account created successfully')
        return redirect('feed:feed')
