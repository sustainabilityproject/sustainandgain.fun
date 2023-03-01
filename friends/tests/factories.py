from django.db.models.signals import post_save

import friends.models 
import factory
from django.contrib.auth import get_user_model

@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    """
    Generate a user with random first and second names, email {first_name}.{second_name}@example.com,
    username {first_name}n where n increments for each user.
    """
    class Meta:
        model = get_user_model()

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda a: "{}.{}@example.com".format(a.first_name, a.last_name).lower())

    @factory.lazy_attribute_sequence
    def username(self, n):
        return "{}{}".format(self.first_name, n)

@factory.django.mute_signals(post_save)
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = friends.models.Profile

    user = factory.SubFactory(UserFactory)


class FriendRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = friends.models.FriendRequest

    from_profile = factory.SubFactory(ProfileFactory)
    to_profile = factory.SubFactory(ProfileFactory)
    status = 'p'

    