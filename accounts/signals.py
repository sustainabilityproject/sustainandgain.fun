from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import os

from accounts.models import User
from friends.models import Profile


# Auto create a profile for each user
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# when adding profile picture checks if the picture is the same and deletes the old one
@receiver(pre_save, sender=Profile)
def delete_old_file(sender, instance, **kwargs):
    # on creation, signal callback won't be triggered 
    if instance._state.adding and not instance.pk:
        return False
    
    try:
        old_file = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return False
    
    # comparing the new file with the old one, checking if old one is the default
    
    file = instance.image
    if old_file != file:
        if old_file.path != Profile().image.path:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)