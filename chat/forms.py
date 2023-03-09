from django import forms
from .models import ChatMessage

class ChatMessageForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Enter message...', 'class': 'form-control'}))

    class Meta:
        model = ChatMessage
        fields = ['content']
