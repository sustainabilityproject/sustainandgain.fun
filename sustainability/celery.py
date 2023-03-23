import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainability.settings')

app = Celery('sustainability')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Run assign_tasks every day at 11:00 AM
app.conf.beat_schedule = {
    'assign_task': {
        'task': 'assign_tasks',
        'schedule': crontab(hour=11, minute=00),
    },
}
