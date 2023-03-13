import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from imagenet.apps import feature_extractor, model
from sustainability.settings import BASE_DIR
from tasks.models import TaskInstance
from PIL import Image, ImageOps


# When a task is saved, check if it is a coffee task
@receiver(post_save, sender=TaskInstance)
def task_autocomplete(sender, instance, created, **kwargs):
    """
    When a task is saved, check if it is a coffee task.
    If it is, run the AI model to see if the photo is of a coffee mug.

    Attributes:
        sender: The model that sent the signal.
        instance: The instance of the model that was saved.
        created: Whether the instance was created or updated.
        kwargs: Any additional keyword arguments.
    """

    # If the task has a photo, is not completed, and is a coffee task, run the AI model
    if instance.ai_tag is None and instance.photo and instance.status != instance.COMPLETED and \
            ("coffee" in instance.task.title.lower() or "caffeine" in instance.task.title.lower()):
        import torch
        with Image.open(os.path.join(BASE_DIR, "media", instance.photo.name), 'r') as img:
            # get dimensions of image
            width, height = img.size

            # calculate coordinates for cropping
            left = (width - min(width, height)) // 2
            upper = (height - min(width, height)) // 2
            right = left + min(width, height)
            lower = upper + min(width, height)

            # crop the image
            img = img.crop((left, upper, right, lower))

            # resize the image to 224x224
            img = img.resize((224, 224))

            # fix orientation metadata using ImageOps.exif_transpose()
            img = ImageOps.exif_transpose(img)

            assert feature_extractor is not None, "feature_extractor model is not loaded"
            assert img is not None, "img variable is None"

            inputs = feature_extractor(img, return_tensors="pt")

            with torch.no_grad():
                logits = model(**inputs).logits

            predicted_label = logits.argmax(-1).item()
            print(model.config.id2label[predicted_label])

            # Save the tag even if not a coffee mug so that it is not run again
            instance.ai_tag = model.config.id2label[predicted_label]
            if model.config.id2label[predicted_label] in ["coffee mug", "cup", "espresso"]:
                instance.status = instance.COMPLETED

            instance.save()
