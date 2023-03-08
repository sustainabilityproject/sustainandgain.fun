from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse


from .models import Notifications
# Create your views here.

def index(request):
    return render(request, 'notifications/index.html')

def delete_notification(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        notification = Notifications.objects.get(notification_id=notification_id)
        notification.delete()
        next_url = request.POST.get('next', None)
        if next_url:
            return redirect(next_url)
    return redirect(reverse('notifications'))