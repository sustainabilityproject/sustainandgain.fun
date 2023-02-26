from django.views.generic import ListView
from tasks.models import TaskInstance
from django.db.models import Q


class FeedView(ListView):
    template_name = 'feed/feed.html'
    context_object_name = 'completed_tasks'
    model = TaskInstance

    def get_queryset(self):
        tasks = TaskInstance.objects.exclude(Q(status=TaskInstance.ACTIVE))
        return tasks