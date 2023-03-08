from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models

from tasks.models import TaskInstance
from notifications.models import Notifications


class League(models.Model):
    """
    A League is a group of users who can compete against each other.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(default='', blank=True, max_length=500)
    members = models.ManyToManyField('friends.Profile', through='LeagueMember')

    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    # A league can either be public (anyone can view it) or private (only members can view it)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')

    # Invite-only: user must request to join or can be invited by an admin
    invite_only = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_members(self):
        return self.leaguemember_set.filter(status='joined')

    def get_invited_members(self):
        return self.leaguemember_set.filter(status='invited')

    def get_pending_members(self):
        return self.leaguemember_set.filter(status='pending')

    def get_ranked_members(self):
        members = self.leaguemember_set.filter(status='joined')
        members = sorted(members, key=lambda member: member.total_points(), reverse=True)
        return members

    def add_admin(self, profile):
        """
        Add a user as an admin of the league.
        """
        member, created = LeagueMember.objects.get_or_create(league=self, profile=profile)
        member.role = 'admin'
        member.status = 'joined'
        member.save()

    def join(self, request, profile):
        """
        Join the league as a member.
        """

        profiles = [member.profile for member in self.get_members()]
        if profile in profiles:
            raise ValidationError('You are already a member of this league')

        if self.invite_only:
            # If the user hasn't been invited, change their status to pending
            if not LeagueMember.objects.filter(league=self, profile=profile, status='invited').exists():
                member, created = LeagueMember.objects.get_or_create(league=self, profile=profile)
                member.status = 'pending'
                member.save()
                if request is not None:
                    messages.success(request, f'You have requested to join {self.name}')
                return

        # If the user has been invited or the league is public, add them to the league
        member, created = LeagueMember.objects.get_or_create(league=self, profile=profile)
        member.status = 'joined'
        member.save()
        if request is not None:
            messages.success(request, f'You have joined {self.name}')
        return

    def invite(self, request, profile):
        """
        Invite a user to join the league.
        """

        profiles = [member.profile for member in self.get_members()]
        if profile in profiles:
            raise ValidationError('Already a member of this league')

        # If the user is pending, change their status to joined
        if LeagueMember.objects.filter(league=self, profile=profile, status='pending').exists():
            member = LeagueMember.objects.get(league=self, profile=profile)
            member.status = 'joined'
            member.save()
            if request is not None:
                messages.success(request, f'{profile.user.username} has joined {self.name}')
            return 'joined'
        else:
            member, created = LeagueMember.objects.get_or_create(league=self, profile=profile)
            member.status = 'invited'
            member.save()
            if request is not None:
                messages.success(request, f'{profile.user.username} has been invited to join {self.name}')

            # Send a notification to the user
            if request is not None:
                Notifications.objects.create(
                    notification_type='league_invite',
                    notification_message=f'You have been invited to join {self.name} by {request.user.username}',
                    notification_user=profile.user,
                    notification_url=f'/leagues/{self.id}/',
                )
            return

    def promote(self, request, profile):
        """
        Promote a user to admin.
        """
        member, created = LeagueMember.objects.get_or_create(league=self, profile=profile)
        member.role = 'admin'
        member.save()
        if request is not None:
            messages.success(request, f'{profile.user.username} has been promoted to admin')
        return

    def demote(self, request, profile):
        """
        Demote a user from admin.
        """
        # If the user is the only admin, they cannot be demoted
        if LeagueMember.objects.filter(league=self, role='admin').count() == 1:
            raise ValidationError('You are the only admin of this league. You cannot be demoted.')
        member, created = LeagueMember.objects.get_or_create(league=self, profile=profile)
        member.role = 'member'
        member.save()
        if request is not None:
            messages.success(request, f'{profile.user.username} has been demoted to member')
        return

    def leave(self, request, profile):
        """
        Leave the league.
        """
        member = LeagueMember.objects.get(league=self, profile=profile)
        if profile not in self.members.all():
            raise ValidationError('You are not a member of this league')

        if member.role == 'admin' and LeagueMember.objects.filter(league=self, role='admin').count() == 1:
            raise ValidationError('You are the only admin of this league. You cannot leave.')

        if member.status == 'invited':
            member.delete()
            if request is not None:
                messages.success(request, f'You have declined the invitation to {self.name}')
            return

        if member.status == 'pending':
            member.delete()
            if request is not None:
                messages.success(request, f'You have removed your request to join {self.name}')
            return

        member.delete()
        if request is not None:
            messages.success(request, f'You have left {self.name}')
        return

    def kick(self, request, profile):
        """
        Kick a user from the league.
        """
        member = LeagueMember.objects.get(league=self, profile=profile)
        if profile not in self.members.all():
            raise ValidationError('User is not a member of this league')

        if member.role == 'admin' and LeagueMember.objects.filter(league=self, role='admin').count() == 1:
            raise ValidationError('You are the only admin of this league. You cannot kick.')

        member.delete()
        if request is not None:
            messages.success(request, f'{profile.user.username} has been kicked from {self.name}')
        return

    def clean(self):
        # If the league is private, it must be invite-only
        if self.visibility == 'private' and not self.invite_only:
            raise ValidationError('Private leagues must be invite-only')
        return self


class LeagueMember(models.Model):
    """
    A LeagueMember is a user who is a member of a league.
    """
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    profile = models.ForeignKey('friends.Profile', on_delete=models.CASCADE)

    """
    Invited: user has been invited to join the league by an admin
    Pending: user has requested to join an invite-only league
    Joined: user is a member of the league
    """
    status = models.CharField(max_length=20, choices=(('invited', 'Invited'),
                                                      ('joined', 'Joined'), ('pending', 'Pending')), default='pending')

    role = models.CharField(max_length=20, choices=(
        ('member', 'Member'),
        ('admin', 'Admin'),
    ), default='member')

    def __str__(self):
        return f'{self.profile.user.username} in {self.league.name}'

    def total_points(self):
        task_instances = TaskInstance.objects.filter(profile=self.profile, status=TaskInstance.COMPLETED)
        total_points = 0
        for task_instance in task_instances:
            total_points += task_instance.task.points
        return total_points
