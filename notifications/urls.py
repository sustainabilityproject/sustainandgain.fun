from django.urls import path
from .views import delete_notification

app_name = 'notifications'

urlpatterns = [
    path('delete-notification/', delete_notification, name='delete_notification'),
]