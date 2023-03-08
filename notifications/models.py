from django.db import models

# Create your models here.

class Notifications(models.Model):
    """
    Notifications store information about important events that have happened in the system.

    Attributes:
        notification_id (int): The primary key for the notification
        notification_type (str): The type of notification
        notification_message (str): The message to be displayed to the user
        notification_date (datetime): The date and time the notification was created
        notification_user (int): The user who the notification is for

    Methods:
        __str__: Returns the notification message

    """
    notification_id = models.AutoField(primary_key=True)
    notification_type = models.CharField(max_length=50)
    notification_message = models.CharField(max_length=100)
    notification_date = models.DateTimeField(auto_now_add=True)
    notification_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    notification_url = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.notification_message

    def get_user_notifications(self, user_id):
        """
        Get all notifications for a user

        :param user_id: The user id of the user to get notifications for
        :return: A list of notifications
        """
        return Notifications.objects.filter(notification_user=user_id).order_by('-notification_date')
    
class Meta:
    """
    Meta class for the notifications model

    Attributes:
        db_table (str): The name of the database table to use for the model
        verbose_name (str): The singular name to use when referring to the model
        verbose_name_plural (str): The plural name to use when referring to the model

    """
    db_table = 'notifications'
    verbose_name = 'Notification'
    verbose_name_plural = 'Notifications'
