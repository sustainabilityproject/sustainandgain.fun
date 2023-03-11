from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from notifications.signals import notify

from friends.models import FriendRequest


@receiver(post_save, sender=FriendRequest)
def send_friend_request_notification(sender, instance, created, **kwargs):
    if created:
        notify.send(instance.from_profile, recipient=instance.to_profile.user, verb='sent you a friend request.',
                    action_object=instance, target=instance.to_profile, url=reverse('friends:list'), public=False)
        
    if not created and instance.status == 'a':
        notify.send(instance.to_profile, recipient=instance.from_profile.user, verb='accepted your friend request.',
                    action_object=instance, target=instance.from_profile, url=reverse('friends:list'), public=False)