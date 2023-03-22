from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from notifications.signals import notify

from tasks.models import TaskInstance


@receiver(post_save, sender=TaskInstance)
def send_tag_notification(sender, instance, created, **kwargs):
    """
    Send user a notification when they have been tagged in a task.
    Applicable when another user or Steve tagged.
    """
    if 'tagged you' in instance.origin_message:
        notify.send(instance.profile, recipient=instance.profile.user, verb='tagged you in a task.',
                    action_object=instance, target=instance.task, url=reverse('tasks:list'), public=False)
