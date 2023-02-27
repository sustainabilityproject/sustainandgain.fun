from django.views.generic import ListView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from tasks.models import TaskInstance


class FeedView(ListView):
    template_name = 'feed/feed.html'
    context_object_name = 'completed_tasks'
    model = TaskInstance

    def get_queryset(self):
        tasks = TaskInstance.objects.exclude(status=TaskInstance.ACTIVE)
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
        return redirect('feed:feed')
    

class ReportView(TemplateView):
    template_name = 'feed/report.html'

    def get(self, request, pk):
        return redirect('feed:feed')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        task.reports.add(request.user.profile)
        task.save()
        messages.success(request, 'You reported this post')
        return redirect('feed:feed')
