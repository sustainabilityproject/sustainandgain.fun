from django.db import models
from django. contrib. auth. models import User
from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_with')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_received')
    message = models.CharField(max_length=255, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}: {self.status}'

    class Meta:
        unique_together = ('from_user', 'to_user')


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username
