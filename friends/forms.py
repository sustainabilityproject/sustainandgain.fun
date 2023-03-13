import os

from django import forms

from .models import Profile


class UpdateProfileForm(forms.ModelForm):
    """
    Form to update user profile.

    Attributes:
        first_name (CharField): The first name displayed.
        last_name (CharField): The last name displayed.

    Methods:
        __init__(self, *args, **kwargs): TODO
        save(self, commit): Save changes to the profile.
    """
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        """
        TODO
        """
        model = Profile
        fields = ['first_name', 'last_name', 'image', 'bio']

    def __init__(self, *args, **kwargs):
        """
        TODO
        """
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        """
        Save changes to the profile.
        Assign path to image.

        Returns:
            profile (Profile): The updated profile.
        """
        profile = super().save(commit=False)
        current_image = Profile.objects.get(user=self.instance.user).image
        if self.cleaned_data['image'] != current_image:
            current_image.delete()
            profile.image.name = f'{profile.user.username}{os.path.splitext(self.cleaned_data["image"].name)[1]}'
        else:
            profile.image = current_image

        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        if commit:
            profile.user.save()
            profile.save()
        return profile
