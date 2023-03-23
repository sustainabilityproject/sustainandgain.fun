from celery import shared_task
from tasks.management.commands.assigntasks import Command as AssignTask


@shared_task(name="assign_tasks")
def assign_tasks():
    """
    Celery task to assign tasks to users which is run every day at 11:00 AM.
    See sustainability/celery.py for more information.
    """
    AssignTask().handle()
    return None
