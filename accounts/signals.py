from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import os

from accounts.models import User
from friends.models import Profile, FriendRequest


# Auto create a profile for each user
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        sussteve = User.objects.get(username='SusSteve')
        FriendRequest.objects.create(from_profile=sussteve.profile, to_profile=instance.profile, status='p')
