from django import forms
from .models import Profile

class UpdateProfileImage(forms.ModelForm):

    type = 'profile'

    class Meta:
        model = Profile
        fields = ("image",)

class UpdateProfileBio(forms.ModelForm):

    type = 'bio'

    class Meta:
        model = Profile
        fields = ("bio",)
