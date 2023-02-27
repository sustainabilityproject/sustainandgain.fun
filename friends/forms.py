from django import forms
from .models import Profile

class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ("image","bio")
