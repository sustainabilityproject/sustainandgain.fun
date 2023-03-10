from django.db import models, IntegrityError
from django.db.models import Q

from accounts.models import User



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # single profile image
    image = models.ImageField(default='default/default.jpg', upload_to='profile_pics')
    friends = models.ManyToManyField('self', blank=True, symmetrical=True, through='FriendRequest')
    bio = models.TextField(default='', blank=True)

    def __str__(self):
        return f'{self.user.username}'

    def get_friends(self, status='a'):
        """
        Returns a list of friends where the request has status specified by the status parameter
        a = accepted
        p = pending
        all = both a and p requests
        """
        if status != 'all':
            friends = [
                request.to_profile if (request.from_profile == self) else request.from_profile 
                for request in FriendRequest.objects.filter(Q(from_profile=self) | Q(to_profile=self), status=status)
                ]
        else:
            friends = [
                request.to_profile if (request.from_profile == self) else request.from_profile 
                for request in FriendRequest.objects.filter(Q(from_profile=self) | Q(to_profile=self))
                ]

        return list(set(friends))
    
    def get_friends_and_requested_friends(self):
        """
        Returns dictionary populated with the profiles of the current profile's friends, incoming pending friends and outgoing pending friends in lists

                Return:
                        dict_of_friends (Dict[str, List[Profile]]): keys: 'a': list of accepted friends profiles 
                                                                          'in_p': list of profiles from incoming friend requests
                                                                          'out_p': list of profiles from outgoing friend requests
        """

        accepted_friends = []
        in_pending_friends = []
        out_pending_friends = []

        for request in FriendRequest.objects.filter(Q(from_profile=self) | Q(to_profile=self)):
            if request.status == 'a':
                if request.to_profile != self:
                    accepted_friends.append(request.to_profile)
                else:
                    accepted_friends.append(request.from_profile)
            else:
                if request.to_profile == self:
                    in_pending_friends.append(request.from_profile)
                else:
                    out_pending_friends.append(request.to_profile)

        dict_of_friends = {'a': accepted_friends, 'in_p': in_pending_friends, 'out_p': out_pending_friends}
        return dict_of_friends

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
