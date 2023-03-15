from django.db import models
from django.conf import settings

# Create your models here.

from django.contrib.auth.models import User
from tasks.models import TaskInstance


class Comment(models.Model):
    task_instance = models.ForeignKey(TaskInstance, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL instead of User directly
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
