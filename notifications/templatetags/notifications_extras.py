from django import template
from notifications.models import Notifications

register = template.Library()

# Gets the notifications associated with a user's id
@register.simple_tag
def get_user_notifications(user):
        """
        Get all notifications for a user

        :param user: The user to get notifications for
        :return: A list of notifications
        """
        return Notifications.objects.filter(notification_user=user).order_by('-notification_date')

# Gets the number of notifications associated with a user's id
@register.simple_tag
def get_unread_count(user):
        """
        Get the number of unread notifications for a user

        :param user: The user to get notifications for
        :return: The number of unread notifications
        """
        return Notifications.objects.filter(notification_user=user).count()