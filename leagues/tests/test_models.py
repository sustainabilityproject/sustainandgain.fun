from unittest import TestCase

from django.core.exceptions import ValidationError, ObjectDoesNotExist

from friends.tests.factories import ProfileFactory
from leagues.tests.factories import LeagueFactory


# Test if a user can join a league
class OpenLeagueMemberJoin(TestCase):
    def setUp(self):
        self.league_instance = LeagueFactory()
        self.profile_instance = ProfileFactory()

    def tearDown(self):
        self.league_instance.delete()
        self.profile_instance.user.delete()
        self.profile_instance.delete()

    def test_join(self):
        self.league_instance.join(None, self.profile_instance)
        league_member = self.league_instance.leaguemember_set.get(profile=self.profile_instance)
        self.assertEqual(league_member.status, 'joined')

    def test_join_twice(self):
        self.league_instance.join(None, self.profile_instance)
        with self.assertRaises(ValidationError):
            self.league_instance.join(None, self.profile_instance)


class InviteOnlyLeagueMemberJoin(TestCase):

    def setUp(self):
        self.league_instance = LeagueFactory(invite_only=True)
        self.profile_instance = ProfileFactory()

    def tearDown(self):
        self.league_instance.delete()
        self.profile_instance.user.delete()
        self.profile_instance.delete()

    def test_join_invite_only(self):
        self.league_instance.invite_only = True
        self.league_instance.save()
        self.league_instance.join(None, self.profile_instance)
        league_member = self.league_instance.leaguemember_set.get(profile=self.profile_instance)
        self.assertEqual(league_member.status, 'pending')

    def test_join_invite_only_invited(self):
        self.league_instance.invite_only = True
        self.league_instance.save()
        self.league_instance.invite(None, self.profile_instance)
        self.league_instance.join(None, self.profile_instance)
        league_member = self.league_instance.leaguemember_set.get(profile=self.profile_instance)
        self.assertEqual(league_member.status, 'joined')


class InviteOnlyLeagueMemberInvite(TestCase):

    def setUp(self):
        self.league_instance = LeagueFactory(invite_only=True)
        self.profile_instance = ProfileFactory()

    def test_invite(self):
        self.league_instance.invite(None, self.profile_instance)
        league_member = self.league_instance.leaguemember_set.get(profile=self.profile_instance)
        self.assertEqual(league_member.status, 'invited')

    def tearDown(self):
        self.league_instance.delete()
        self.profile_instance.user.delete()
        self.profile_instance.delete()


class PromoteDemoteLeagueMember(TestCase):

    def setUp(self):
        self.league_instance = LeagueFactory()
        self.profile_instance = ProfileFactory()

    def test_promote(self):
        self.league_instance.join(None, self.profile_instance)
        self.league_instance.promote(None, self.profile_instance)
        league_member = self.league_instance.leaguemember_set.get(profile=self.profile_instance)
        self.assertEqual(league_member.role, 'admin')

    def test_demote(self):
        self.league_instance.join(None, self.profile_instance)
        self.profile_instance2 = ProfileFactory()
        self.league_instance.join(None, self.profile_instance2)
        # Need to promote two so that we can demote one as there must always be at least one admin
        self.league_instance.promote(None, self.profile_instance)
        self.league_instance.promote(None, self.profile_instance2)
        self.league_instance.demote(None, self.profile_instance)
        league_member = self.league_instance.leaguemember_set.get(profile=self.profile_instance)
        self.assertEqual(league_member.role, 'member')
        self.profile_instance2.user.delete()
        self.profile_instance2.delete()

    def test_demote_only_admin(self):
        self.league_instance.join(None, self.profile_instance)
        self.league_instance.promote(None, self.profile_instance)
        with self.assertRaises(ValidationError):
            self.league_instance.demote(None, self.profile_instance)

    def tearDown(self):
        self.league_instance.delete()
        self.profile_instance.user.delete()
        self.profile_instance.delete()


class LeagueMemberLeave(TestCase):

    def setUp(self):
        self.league_instance = LeagueFactory()
        self.profile_instance = ProfileFactory()

    def test_leave(self):
        self.league_instance.join(None, self.profile_instance)
        self.league_instance.leave(None, self.profile_instance)
        with self.assertRaises(ObjectDoesNotExist):
            self.league_instance.leaguemember_set.get(profile=self.profile_instance)

    def tearDown(self):
        self.league_instance.delete()
        self.profile_instance.user.delete()
        self.profile_instance.delete()


class LeagueMemberKick(TestCase):

    def setUp(self):
        self.league_instance = LeagueFactory()
        self.profile_instance = ProfileFactory()
        self.league_instance.join(None, self.profile_instance)

    def test_kick(self):
        self.league_instance.kick(None, self.profile_instance)
        with self.assertRaises(ObjectDoesNotExist):
            self.league_instance.leaguemember_set.get(profile=self.profile_instance)

    def test_kick_non_member(self):
        self.profile_instance2 = ProfileFactory()
        with self.assertRaises(ObjectDoesNotExist):
            self.league_instance.kick(None, self.profile_instance2)
        self.profile_instance2.user.delete()
        self.profile_instance2.delete()

    def tearDown(self):
        self.league_instance.delete()
        self.profile_instance.user.delete()
        self.profile_instance.delete()
