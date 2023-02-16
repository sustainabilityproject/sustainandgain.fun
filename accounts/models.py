from django.db import models
from django. contrib. auth. models import User
from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username
