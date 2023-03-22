from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from friends.models import Profile, FriendRequest


# Auto create a profile for each user
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new profile for the user
        Profile.objects.create(user=instance)
        # Send a friend request to the user from Sustainability Steve
        steve = User.objects.get(username='SusSteve')
        FriendRequest.objects.create(from_profile=steve.profile, to_profile=instance.profile, status='p')
