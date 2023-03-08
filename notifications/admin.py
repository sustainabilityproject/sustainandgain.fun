from django.contrib import admin

# Register your models here.

from notifications.models import Notifications

class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'notification_type', 'notification_message', 'notification_date', 'notification_user')

admin.site.register(Notifications, NotificationsAdmin)