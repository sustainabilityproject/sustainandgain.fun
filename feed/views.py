import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, UpdateView
from django.views.generic import TemplateView

from tasks.models import TaskInstance


class FeedView(LoginRequiredMixin, ListView):
    """
    View for the feed page. Shows all tasks that have been completed by the user or their friends.
    """
    template_name = 'feed/feed.html'
    context_object_name = 'friend_tasks'
    model = TaskInstance

    def get_queryset(self):
        tasks = TaskInstance.objects.exclude(status=TaskInstance.ACTIVE)
        # Only show tasks of the user or their friends.
        tasks = [task for task in tasks if
                 task.profile == self.request.user.profile or task.profile in self.request.user.profile.get_friends()]
        # If a task was completed more than a week ago, its status is set to COMPLETED
        for task in tasks:
            if task.status == TaskInstance.PENDING_APPROVAL and datetime.datetime.now() > task.time_completed.replace(
                    tzinfo=None) + datetime.timedelta(days=7):
                task.status = TaskInstance.COMPLETED
                task.save()

        # Sort tasks by time completed, most recent first
        tasks.sort(key=lambda x: x.time_completed, reverse=True)

        return tasks


class HomeView(TemplateView):
    """
    View for the home page. Redirects to the feed if the user is logged in, otherwise shows the home page.
    """
    template_name = "home.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('feed:feed')
        return super().get(request)


class ReportTaskView(LoginRequiredMixin, UpdateView):
    """
    View for reporting a task. If the user is a staff member, the task is deleted. Otherwise, the task is reported and
    a staff member will review it.
    """

    def get(self, request, pk):
        return redirect('feed:feed')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        if request.user.is_staff:
            task.delete()
            messages.success(request, 'You deleted a task.')
        else:
            task.reports.add(request.user.profile)
            task.save()
            messages.success(request, 'You reported a task.')

        return redirect('feed:feed')


class LikeTaskView(LoginRequiredMixin, UpdateView):
    """
    View for liking a task. If the task gets 3 likes, it is approved.
    """

    def get(self, request, pk):
        return redirect('feed:feed')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        if request.user.profile == task.profile:
            messages.info(request, "You can't like your own task.")
            return redirect('feed:feed')

        else:
            task.likes.add(request.user.profile)
            task.save()
            if task.likes.count() >= 3:
                task.status = TaskInstance.PENDING_APPROVAL
                task.save()
            messages.success(request, 'You liked a task.')
            return redirect('feed:feed')


# Staff views

class ReportedTasksView(LoginRequiredMixin, ListView):
    """
    View for the reported tasks page. Shows all tasks that have been reported by users. Staff only.
    """
    template_name = 'feed/reported_tasks.html'
    context_object_name = 'reported_tasks'
    model = TaskInstance

    # User must be a staff member to view reported tasks
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('feed:feed')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        tasks = TaskInstance.objects.all()
        tasks = [task for task in tasks if task.reports.count() > 0]

        return tasks


class DeleteTaskView(LoginRequiredMixin, UpdateView):
    """
    View for deleting a task. Staff only.
    """

    # User must be a staff member to delete a task
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('feed:reported')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return redirect('feed:reported')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        task.delete()
        messages.success(request, 'You deleted a task.')
        return redirect('feed:reported')


class RestoreTaskView(LoginRequiredMixin, UpdateView):
    """
    View for restoring a reported task. Staff only.
    """

    # User must be a staff member to restore a task
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('feed:reported')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return redirect('feed:reported')

    def post(self, request, pk):
        task = get_object_or_404(TaskInstance, pk=pk)
        task.reports.clear()
        task.status = TaskInstance.COMPLETED
        task.save()
        messages.success(request, 'You restored a task.')
        return redirect('feed:reported')
