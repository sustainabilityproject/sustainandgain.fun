from background_task import background


@background
def assign_tasks():
    from django.core import management
    management.call_command('assigntasks')
