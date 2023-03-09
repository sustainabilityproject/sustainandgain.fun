from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
from leagues.models import LeagueMember


@receiver(post_save, sender=LeagueMember)
def send_league_notification(sender, instance, created, **kwargs):
    admins = instance.league.get_admins()
    if created and instance.status == 'pending':
        for admin in admins:
            notify.send(instance.profile, recipient=admin.profile.user, verb='requested to join your league.',
                        action_object=instance, target=instance.league, url=instance.league.get_absolute_url(), public=False)

    if not created and instance.status == 'joined':
        for admin in admins:
            notify.send(instance.profile, recipient=admin.profile.user, verb='joined your league.',
                        action_object=instance, target=instance.league, url=instance.league.get_absolute_url(), public=False)

    if not created and instance.status == 'invited':
        notify.send(instance.profile, recipient=instance.profile.user, verb='invited you to join their league.',
                    action_object=instance, target=instance.league, url=instance.league.get_absolute_url(), public=False)