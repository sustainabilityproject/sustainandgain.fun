from django import template
from tasks.models import TaskInstance

register = template.Library()

# Gets the total number of tasks that have been reported at least once.
@register.simple_tag
def get_reported_count():
    tasks = TaskInstance.objects.all()
    tasks = [task for task in tasks if task.reports.count() > 0]
    return len(tasks)
