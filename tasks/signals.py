from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from notifications.signals import notify

from tasks.models import TaskInstance


# Notify a user when they are tagged with a task
@receiver(post_save, sender=TaskInstance)
def send_tag_notification(sender, instance, created, **kwargs):
    if 'tagged you' in instance.origin_message:
        notify.send(instance.profile, recipient=instance.profile.user, verb='tagged you in a task.',
                    action_object=instance, target=instance.task, url=reverse('tasks:list'), public=False)
