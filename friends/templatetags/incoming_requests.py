from django import template
from friends.models import FriendRequest

register = template.Library()


@register.simple_tag
def get_friend_requests(user):
    """
    Get the total number of incoming friend requests using a django template tag.

    Args:
        user (User): The user to search.

    Returns:
        int: Number of incoming friend requests.
    """
    friend_requests = FriendRequest.objects.filter(to_profile=user, status='p').values_list(
            'from_profile_id', flat=True)
    return friend_requests.count()
