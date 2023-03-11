from django.db import models

from accounts.models import User


class ChatMessage(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content + ' - ' + self.author.profile.name
