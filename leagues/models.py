from django.db import models


class League(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    members = models.ManyToManyField('friends.Profile', related_name='leagues', blank=True)

    def ranked_members(self):
        members = self.members.all()
        ranked_members = sorted(members, key=lambda member: member.total_points(), reverse=True)
        return ranked_members

    def __str__(self):
        return self.name
