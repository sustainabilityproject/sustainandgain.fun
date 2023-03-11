import re, os
from django import forms
from .models import ChatMessage
from pathlib import Path
from better_profanity import profanity

def sanitize_input(input_str):
    pattern = re.compile(r"[^A-Za-z0-9\s\.\,\?\!\-\(\)\[\]\{\}\:\;\"\'\`]", re.IGNORECASE)
    input_str = pattern.sub("", input_str)
    return profanity.censor(input_str, '*')
    

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