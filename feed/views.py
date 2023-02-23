from django.views.generic import ListView
from tasks.models import TaskInstance


class FeedView(ListView):
    template_name = 'feed/feed.html'
    context_object_name = 'completed_tasks'
    queryset = TaskInstance.objects.filter(status='COMPLETED')
