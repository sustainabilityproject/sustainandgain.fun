from django.views.generic import ListView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from .models import ChatMessage
from .forms import ChatMessageForm


class ChatView(LoginRequiredMixin, ListView, FormView):
    """
    View of the global chat.

    Attributes:
        model (ChatMessage): The thing being displayed.
        template_name (str): The html template this view uses.
        form_class (ChatMessageForm): The form used to interact.
        success_url: Where forms redirect.

    Methods:
        get_queryset(self): Return the 50 most recent messages in order, newest to oldest.
        form_valid(self, form): Sets the form's author to the user and save it when valid data is POSTed.
        get_context_data(self, **kwargs):
    """
    model = ChatMessage
    template_name = 'chat.html'
    form_class = ChatMessageForm
    success_url = reverse_lazy('chat')

    def get_queryset(self):
        """
        Return the 50 most recent messages in order, newest to oldest.

        Returns:
            QuerySet[ChatMessage]: Messages sent in the chat.
        """
        return ChatMessage.objects.order_by('timestamp')[:50]

    def form_valid(self, form):
        """
        Sets the form's author to the user and save it when valid data is POSTed.

        Returns:
           HttpResponseRedirect(success_url): an HTTP redirection to the form's success_url.

        """
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Return the 50 most recent messages in order, newest to oldest.

        Returns:
            context(dict[str, ChatMessage]): Messages sent in the chat.
        """
        context = super().get_context_data(**kwargs)
        queryset = ChatMessage.objects.order_by('-timestamp')[:50]
        if isinstance(queryset, QuerySet):
            context['submitted_messages'] = list(queryset)
        else:
            context['submitted_messages'] = []
        return context
