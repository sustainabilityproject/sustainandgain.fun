from django.core.exceptions import ValidationError
from django.db import models

from tasks.models import TaskInstance


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
