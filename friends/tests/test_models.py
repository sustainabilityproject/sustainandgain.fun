from django.core.exceptions import ValidationError
from django.test import TestCase

from friends.models import *
from friends.tests.factories import ProfileFactory, FriendRequestFactory


class FriendRequestIntegrity(TestCase):

    # test for IntegrityError if a user tries to make a request twice
    def test_failed_request_twice(self):
        to_profile_instance = ProfileFactory.create()
        from_profile_instance = ProfileFactory.create()
        request = FriendRequestFactory.create(
            to_profile=to_profile_instance,
            from_profile=from_profile_instance)
        with self.assertRaises(ValidationError):
            FriendRequestFactory.create(
                to_profile=to_profile_instance,
                from_profile=from_profile_instance
            )

    # test for IntegrityError if user makes request to user who has sent them one already
    def test_failed_request_made_other_way(self):
        to_profile_instance = ProfileFactory.create()
        from_profile_instance = ProfileFactory.create()
        request = FriendRequestFactory.create(
            to_profile=to_profile_instance,
            from_profile=from_profile_instance
        )
        with self.assertRaises(IntegrityError):
            FriendRequestFactory.create(
                to_profile=from_profile_instance,
                from_profile=to_profile_instance
            )

    # test for IntegrityError if user makes request to self
    def test_failed_request_to_self(self):
        to_profile_instance = ProfileFactory.create()
        from_profile_instance = to_profile_instance
        with self.assertRaises(IntegrityError):
            FriendRequestFactory.create(
                to_profile=to_profile_instance,
                from_profile=from_profile_instance
            )


class FriendRequestFunctions(TestCase):

    def test_accept(self):
        profile_instance1 = ProfileFactory()
        profile_instance2 = ProfileFactory()
        request = FriendRequestFactory.create(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        )
        request.accept()
        self.assertEqual(request.status, 'a')
        self.assertEqual(profile_instance1.get_friends().first(), profile_instance2)
        self.assertEqual(profile_instance2.get_friends().first(), profile_instance1)

    def test_decline(self):
        profile_instance1 = ProfileFactory()
        profile_instance2 = ProfileFactory()
        request = FriendRequestFactory.create(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        )
        self.assertEqual(FriendRequest.objects.filter(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        ).first(),
                         request
                         )
        request.delete()
        self.assertIsNone(FriendRequest.objects.filter(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        ).first()
                          )

    def test_cancel(self):
        profile_instance1 = ProfileFactory()
        profile_instance2 = ProfileFactory()
        request = FriendRequestFactory.create(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        )
        self.assertEqual(FriendRequest.objects.filter(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        ).first(),
                         request
                         )
        request.cancel()
        self.assertIsNone(FriendRequest.objects.filter(
            to_profile=profile_instance1,
            from_profile=profile_instance2
        ).first()
                          )


class UserReferenceProfileIntegrity(TestCase):

    def test_cascade_deletion_of_profile_to_user(self):
        profile = ProfileFactory.create()
        user = User.objects.filter(id=profile.id).first()
        self.assertIsNotNone(user)
        # deletes the profile
        profile.delete()
        # tests to see if user has been deleted
        user = User.objects.filter(id=profile.id).first()
        self.assertIsNone(user)
