import datetime
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from tasks.models import TaskInstance


class FeedView(ListView):
    template_name = 'feed/feed.html'
    context_object_name = 'friend_tasks'
    model = TaskInstance

    def get_queryset(self):
        tasks = TaskInstance.objects.exclude(status=TaskInstance.ACTIVE)
        # Only show tasks of the user or their friends
        tasks = [task for task in tasks if task.profile == self.request.user.profile or task.profile in self.request.user.profile.friends.all()]
        # If a task was completed more than a week ago, its status is set to COMPLETED
        for task in tasks:
            if task.status == TaskInstance.PENDING_APPROVAL and datetime.datetime.now() > task.time_completed.replace(tzinfo=None) + datetime.timedelta(days=7):
                task.status = TaskInstance.COMPLETED
                task.save()
        return tasks
    
class HomeView(TemplateView):
    template_name = "home.html"

    def get(self, request):
        if self.request.user.is_authenticated:
            return redirect('feed:feed')
        else:
            return super().get(request)

class LikeView(TemplateView):

    model = TaskInstance

    def get(self, request, pk):
        return redirect('feed:feed')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        task.likes.add(request.user.profile)
        task.save()
        messages.success(request, 'You liked this post')

        # If the task has 3 more likes than reports, it is approved
        if task.likes.count() - task.reports.count() >= 3:
            task.status = TaskInstance.COMPLETED
            task.save()

        return redirect('feed:feed')
    

class ReportView(TemplateView):
    template_name = 'feed/report.html'

    def get(self, request, pk):
        return redirect('feed:feed')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        task.reports.add(request.user.profile)
        task.save()
        messages.success(request, 'You reported this post. An admin will review it shortly.')
        return redirect('feed:feed')
