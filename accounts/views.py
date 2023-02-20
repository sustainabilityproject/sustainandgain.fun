from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import UserCreationForm


class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully')
        return super().form_valid(form)
