from django.db import models


class League(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='', blank=True, max_length=500)
    invite_only = models.BooleanField(default=False)
    members = models.ManyToManyField('friends.Profile', through='LeagueMember')

    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')

    def get_members(self):
        return self.leaguemember_set.filter(status='joined')

    def get_invited_members(self):
        return self.leaguemember_set.filter(status='invited')

    def get_pending_members(self):
        return self.leaguemember_set.filter(status='pending')

    def get_ranked_members(self):
        members = self.leaguemember_set.filter(status='joined')
        ranked_members = sorted(members, key=lambda member: member.profile.total_points(), reverse=True)
        return ranked_members

    def __str__(self):
        return self.name


class LeagueMember(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    profile = models.ForeignKey('friends.Profile', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('invited', 'Invited'),
                                                      ('joined', 'Joined'), ('pending', 'Pending')), default='pending')

    role = models.CharField(max_length=20, choices=(
        ('member', 'Member'),
        ('admin', 'Admin'),
    ), default='member')

    def __str__(self):
        return f'{self.profile.user.username} in {self.league.name}'
