import os

from django import forms

from .models import Profile


class UpdateProfileForm(forms.ModelForm):

    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.cleaned_data['image'] != profile.image:
            profile.image.name = f'{profile.user.username}{os.path.splitext(self.cleaned_data["image"].name)[1]}'

        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        if commit:
            profile.user.save()
            profile.save()
        return profile
