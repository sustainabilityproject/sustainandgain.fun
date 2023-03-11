import os
import uuid

from PIL import Image, ImageOps
from django import forms
from geopy import Nominatim

from sustainability.settings import BASE_DIR
from sustainability.settings import model, feature_extractor, AI
from tasks.models import TaskInstance


class CompleteTaskForm(forms.ModelForm):
    """
    Form for a user to complete a task.
    Allows a user to upload a photo and add a note about the task.
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

        if AI and ("coffee" in task_instance.task.title.lower() or "caffeine" in task_instance.task.title.lower()):
            import torch
            with Image.open(os.path.join(BASE_DIR, "media", task_instance.photo.name), 'r') as img:
                # get dimensions of image
                width, height = img.size

                # calculate coordinates for cropping
                left = (width - min(width, height)) // 2
                upper = (height - min(width, height)) // 2
                right = left + min(width, height)
                lower = upper + min(width, height)

                # crop the image
                img = img.crop((left, upper, right, lower))

                # resize the image to 64x64
                img = img.resize((224, 224))

                # fix orientation metadata using ImageOps.exif_transpose()
                img = ImageOps.exif_transpose(img)

                inputs = feature_extractor(img, return_tensors="pt")

                with torch.no_grad():
                    logits = model(**inputs).logits
                predicted_label = logits.argmax(-1).item()
                if model.config.id2label[predicted_label] == "coffee mug" \
                        or model.config.id2label[predicted_label] == "cup" \
                        or model.config.id2label[predicted_label] == "espresso":
                    task_instance.status = task_instance.COMPLETED
                    task_instance.save()

        return task_instance
