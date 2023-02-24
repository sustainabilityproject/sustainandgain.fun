import os
import uuid

import autoencoder
from PIL import Image, ImageOps
from django import forms

from sustainability.settings import BASE_DIR
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

    def save(self, commit=True):
        """
        Mark the task as Pending Approval and save the photo with a random UUID filename.
        """
        task_instance = super().save(commit=False)
        # Rename the photo to a random UUID to avoid collisions
        task_instance.photo.name = uuid.uuid4().hex + os.path.splitext(task_instance.photo.name)[1]
        task_instance.report_task_complete()
        if commit:
            task_instance.save()

        if "coffee" in task_instance.task.title.lower():
            bin_path = os.path.join(BASE_DIR, "media", "bin", task_instance.photo.name[12:])
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
                img = img.resize((32, 32))

                # fix orientation metadata using ImageOps.exif_transpose()
                img = ImageOps.exif_transpose(img)

                # save the cropped and resized image
                img.save(bin_path)

            confidence = autoencoder.mug_confidence(os.path.join(BASE_DIR),
                                                    os.path.join("/media", "bin", task_instance.photo.name[12:]))

            if os.path.exists(bin_path):
                os.remove(bin_path)
            else:
                print("Failed to delete file")

            print(f"My reconstruction loss: {confidence}")
            if confidence < 0.03:
                task_instance.status = task_instance.COMPLETED
                task_instance.save()

        return task_instance
