from django.db import models
from django.conf import settings

# Create your models here.

from django.contrib.auth.models import User
from tasks.models import TaskInstance


class Comment(models.Model):
    """
    A Comment model representing comments made by users on specific TaskInstances.

    Attributes:
        task_instance (ForeignKey): A foreign key reference to the TaskInstance the comment is related to.
        user (ForeignKey): A foreign key reference to the user who made the comment, using the AUTH_USER_MODEL.
        text (TextField): The text content of the comment.
        created_at (DateTimeField): The timestamp when the comment was created.
    """
    task_instance = models.ForeignKey(TaskInstance, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL instead of User directly
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the Comment model instance.

        Returns:
            str: The text content of the comment.
        """
        return self.text
