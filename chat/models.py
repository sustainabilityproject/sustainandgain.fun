from django.db import models

from accounts.models import User


class ChatMessage(models.Model):
    """
    A message in the global chat.

    Attributes:
        content (TextField): The body of the message.
        author (User): Who posted the message.
        timestamp (DateTimeField): When the message was posted.
    """
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content + ' - ' + self.author.profile.name
