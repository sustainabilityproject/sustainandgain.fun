from django.db import models, IntegrityError

from accounts.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # single profile image
    image = models.ImageField(default='default/default.jpg', upload_to='profile_pics')
    friends = models.ManyToManyField('self', blank=True, symmetrical=True, through='FriendRequest')
    bio = models.TextField(default='', blank=True)

    def __str__(self):
        return f'{self.user.username}'

    def get_friends(self, status='a', id=None):
        """
        Returns a list of friends where the request has status specified by the status parameter
        a = accepted
        p = pending
        """

        friend_requests_sent = FriendRequest.objects.filter(from_profile=self, status=status).values_list(
            'to_profile_id', flat=True)
        friend_requests_received = FriendRequest.objects.filter(to_profile=self, status=status).values_list(
            'from_profile_id', flat=True)
        friend_ids = list(set(friend_requests_sent).union(set(friend_requests_received)))
        friends = Profile.objects.filter(id__in=friend_ids)

        return friends

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name if self.user.first_name else self.user.username


class FriendRequest(models.Model):
    STATUS_CHOICES = (
        ('p', 'Pending'),
        ('a', 'Accepted'),
    )

    from_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_requests_sent')
    to_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p')

    class Meta:
        unique_together = ('from_profile', 'to_profile')

    def __str__(self):
        return f'{self.from_profile} -> {self.to_profile}: {self.status}'

    def accept(self):
        self.status = 'a'
        self.save()
        self.to_profile.friends.add(self.from_profile, through_defaults={'status': 'a'})
        self.from_profile.friends.add(self.to_profile, through_defaults={'status': 'a'})

    def decline(self):
        self.delete()

    def cancel(self):
        self.delete()

    def clean(self):
        from_profile = self.from_profile
        to_profile = self.to_profile
        # raises error if trying to friend self
        if from_profile == to_profile:
            raise IntegrityError("Profile is trying to friend self")
        reverse_request = FriendRequest.objects.filter(to_profile = from_profile, 
                                        from_profile = to_profile
                                        ).first()
        # raises error if request exists going to the other way
        if reverse_request is not None:
            raise IntegrityError("Friend request has been sent the other way")
        
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)
