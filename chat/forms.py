import re, os
from django import forms
from .models import ChatMessage
from pathlib import Path

CURSE_WORDS = ["fuck", "shit", "bitch"]

def sanitize_input(input_str):
    path = Path(__file__).resolve().parent.parent / 'static' / 'en.txt'
    with open(path, 'r') as f:
        swear_words = [line.strip() for line in f]
    for word in swear_words:
        pattern = re.compile(r'\b{}\b'.format(word), re.IGNORECASE)
        input_str = pattern.sub('*' * len(word), input_str)
    return input_str

class ChatMessageForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Enter message...', 'class': 'form-control'}))

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            sanitized_content = sanitize_input(content)
            if not sanitized_content.isascii():
                raise forms.ValidationError('Only English characters are allowed.')
            return sanitized_content
        return content

    class Meta:
        model = ChatMessage
        fields = ['content']

