from django.apps import AppConfig
from transformers import ConvNextForImageClassification, ConvNextImageProcessor


print("Loading AI...")
model = ConvNextForImageClassification.from_pretrained("facebook/convnext-base-224")
feature_extractor = ConvNextImageProcessor.from_pretrained("facebook/convnext-base-224")


class ImagenetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imagenet'

    def ready(self):
        import imagenet.signals
