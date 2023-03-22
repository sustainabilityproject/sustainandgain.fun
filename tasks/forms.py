import os
import uuid

from django import forms
from geopy import Nominatim

from tasks.models import TaskInstance


class CompleteTaskForm(forms.ModelForm):
    """
    Form for a user to complete a task.
    Allows a user to upload a photo and add a note about the task.

    Attributes:
        photo (ImageField): Photo proof that the task was completed.
        note (CharField): Optional caption of the task.
        share_location (BooleanField): Whether the user will share their location.
        latitude (FloatField): User's latitude.
        longitude (FloatField): User's longitude.

    Methods:
        save(self, commit): Mark the task as Pending Approval and save the photo with a random UUID filename.
    """

    class Meta:
        model = TaskInstance
        fields = ['photo', 'note']

    photo = forms.ImageField(required=True, help_text="Required.", label="Photo of completed task")
    note = forms.CharField(required=False, help_text="Optional.", label="Extra notes")
    share_location = forms.BooleanField(required=False, label="Share my location")
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def save(self, commit=True):
        """
        Mark the task as Pending Approval and save the photo with a random UUID filename.

        Returns:
            task_instance (TaskInstance): The completed task instance.
        """
        task_instance = super().save(commit=False)

        current_photo = TaskInstance.objects.get(pk=task_instance.pk).photo
        if current_photo.name != self.instance.photo.name:
            # Rename the photo to a random UUID to avoid collisions
            task_instance.photo.name = uuid.uuid4().hex + os.path.splitext(task_instance.photo.name)[1]
        else:
            task_instance.photo.name = self.instance.photo.name
        task_instance.report_task_complete()

        # Get the address from the latitude and longitude
        if self.cleaned_data.get('share_location'):
            longitude = self.cleaned_data.get('longitude')
            latitude = self.cleaned_data.get('latitude')
            geolocator = Nominatim(user_agent="admin@sustainandgain.fun")
            if longitude is not None and latitude is not None:
                location = geolocator.reverse(f"{latitude}, {longitude}")
                if location.address is not None:
                    task_instance.location = ",".join(location.address.split(",")[:3])

        if commit:
            task_instance.save()

        return task_instance
