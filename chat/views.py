from django.views.generic import ListView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatMessage
from .forms import ChatMessageForm


class ChatView(LoginRequiredMixin, ListView, FormView):
    model = ChatMessage
    template_name = 'chat.html'
    form_class = ChatMessageForm
    success_url = reverse_lazy('chat')

    def get_queryset(self):
        return ChatMessage.objects.order_by('timestamp')[:50]

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submitted_messages'] = ChatMessage.objects.order_by('-timestamp')[:50]
        return context
