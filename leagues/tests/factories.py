import factory
from django.db.models.signals import post_save

from friends.tests.factories import UserFactory, ProfileFactory
from leagues.models import League, LeagueMember


@factory.django.mute_signals(post_save)
class LeagueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = League

    name = factory.Faker("name")
    description = factory.Faker("text")


@factory.django.mute_signals(post_save)
class LeagueMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LeagueMember

    league = factory.SubFactory(LeagueFactory)
    user = factory.SubFactory(UserFactory)
    role = 'member'
    status = 'joined'
