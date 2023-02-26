from django.views.generic import ListView

from tasks.models import TaskInstance


class FeedView(ListView):
    template_name = 'feed/feed.html'
    context_object_name = 'completed_tasks'
    model = TaskInstance

    def get_queryset(self):
        tasks = TaskInstance.objects.exclude(status=TaskInstance.ACTIVE)
        return tasks
