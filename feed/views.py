import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Comment
from django.views import View

from tasks.models import TaskInstance


class FeedView(LoginRequiredMixin, ListView):
    """
    View for the feed page, login required.
    Shows all tasks that have been completed by the user or their friends.

    Attributes:
        template_name (str): The html template this view uses.
        context_object_name (str): What this is called in the template.
        model (TaskInstance): What is being displayed.

    Methods:
        get_queryset(self): Return pending and completed tasks of user's friends, most recent first.
    """
    template_name = 'feed/feed.html'
    context_object_name = 'friend_tasks'
    model = TaskInstance

    def get_queryset(self):
        """
        Return pending and completed tasks of user's friends, most recent first.
        Tasks more than a week old are set to complete.

        Returns:
            tasks (TaskInstance): The tasks to be displayed.
        """
        # Exclude active tasks and exploded tasks
        tasks = TaskInstance.objects.exclude(status=TaskInstance.ACTIVE).exclude(status=TaskInstance.EXPLODED)
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
    View for the home page.
    Redirects to the feed if the user is logged in, otherwise shows the home page.

    Attributes:
        template_name (str): The html template this view uses.

    Methods:
        get(self, request): Sends user to feed if authenticated and home if not.
    """
    template_name = "home.html"

    def get(self, request):
        """
        Send user to feed if authenticated and home if not TODO
        """
        if request.user.is_authenticated:
            return redirect('feed:feed')
        return super().get(request)


class ReportTaskView(LoginRequiredMixin, UpdateView):
    """
    View for reporting a task.
    If the user is a staff member, the task is deleted.
    Otherwise, the task is reported and a staff member will review it.

    Methods:
        get(self, request, pk): Redirect to the feed.
        post(self, request, pk):
    """

    def get(self, request, pk):
        """
        Redirect to the feed. TODO
        """
        return redirect('feed:feed')

    def post(self, request, pk):
        """
        Deletes task if user is staff, otherwise sends task to 'reported tasks' page.

        Returns:
            redirect: Redirects to feed:feed.
        """
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
    View for liking a task.
    If the task gets 3 likes, it is changed from 'pending approval' to 'completed'.

    Methods:
        get(self, request, pk): Redirect to the feed.
        post(self, request, pk): Like someone else's task.
    """

    def get(self, request, pk):
        """
        Redirect to the feed. TODO
        """
        return redirect('feed:feed')

    def post(self, request, pk):
        """
        Like someone else's task.

        Returns:
            redirect: Redirects to feed:feed.
        """
        task = get_object_or_404(TaskInstance, pk=pk)
        if request.user.profile == task.profile:
            messages.info(request, "You can't like your own task.")
            return redirect('feed:feed')

        else:
            task.likes.add(request.user.profile)
            task.save()
            if task.likes.count() >= 3:
                task.status = TaskInstance.COMPLETED
                task.save()
            messages.success(request, 'You liked a task.')
            return redirect('feed:feed')


# Staff views

class ReportedTasksView(LoginRequiredMixin, ListView):
    """
    View for the reported tasks page. Staff only.
    Shows all tasks that have been reported by users.

    Attributes:
        template_name (str): The html template this view uses.
        context_object_name (str): What this is called in the template.
        model (TaskInstance): What is being displayed.

    Methods:
          dispatch(self, request, *args, **kwargs): Redirect to the feed unless the user is staff
          get_queryset(self):
    """
    template_name = 'feed/reported_tasks.html'
    context_object_name = 'reported_tasks'
    model = TaskInstance

    # User must be a staff member to view reported tasks
    def dispatch(self, request, *args, **kwargs):
        """
        Redirect to the feed unless the user is staff
        """
        if not request.user.is_staff:
            return redirect('feed:feed')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return reported tasks.

        Returns:
            tasks (TaskInstance): Tasks which have been reported.
        """
        tasks = TaskInstance.objects.all()
        tasks = [task for task in tasks if task.reports.count() > 0]

        return tasks


class DeleteTaskView(LoginRequiredMixin, UpdateView):
    """
    View for deleting a task. Staff only.

    Methods:
        dispatch(self, request, *args, **kwargs): Redirect to the reported page unless user is staff.
        get(self, request, pk): Redirect to the reported page.
        post(self, request, pk): Delete a task.
    """

    # User must be a staff member to delete a task
    def dispatch(self, request, *args, **kwargs):
        """
        Redirect to the reported page unless user is staff.
        User must be a staff member to delete a task.
        """
        if not request.user.is_staff:
            return redirect('feed:reported')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        """
        Redirect to the reported page. TODO
        """
        return redirect('feed:reported')

    def post(self, request, pk):
        """
        Delete a task.

        Returns:
            redirect: Redirect to the reported page.
        """
        task = get_object_or_404(TaskInstance, pk=pk)
        task.delete()
        messages.success(request, 'You deleted a task.')
        return redirect('feed:reported')


class RestoreTaskView(LoginRequiredMixin, UpdateView):
    """
    View for restoring a reported task. Staff only.

    Methods:
        dispatch(self, request, *args, **kwargs): Redirect to the reported page unless user is staff.
        get(self, request, pk): Redirect to the reported page.
        post(self, request, pk): Set task to 'completed' and remove reports.
    """

    # User must be a staff member to restore a task
    def dispatch(self, request, *args, **kwargs):
        """
        Redirect to the reported page unless user is staff.
        User must be a staff member to restore a task.
        """
        if not request.user.is_staff:
            return redirect('feed:reported')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        """
        Redirect to the reported page. TODO
        """
        return redirect('feed:reported')

    def post(self, request, pk):
        """
        Set task to 'completed' and remove reports.

        Returns:
            redirect: Redirect to the reported page.
        """
        task = get_object_or_404(TaskInstance, pk=pk)
        task.reports.clear()
        task.status = TaskInstance.COMPLETED
        task.save()
        messages.success(request, 'You restored a task.')
        return redirect('feed:reported')



class TaskDetailView(View):
    template_name = 'feed/task_detail.html'

    def get(self, request, task_instance_id):
        task_instance = get_object_or_404(TaskInstance, pk=task_instance_id)
        comments = Comment.objects.filter(task_instance=task_instance).order_by('-created_at')
        context = {'task_instance': task_instance, 'comments': comments}
        return render(request, self.template_name, context)

class CommentView(LoginRequiredMixin, View):
    def post(self, request, task_instance_id):
        task_instance = get_object_or_404(TaskInstance, id=task_instance_id)
        text = request.POST['text']
        
        if text:
            comment = Comment.objects.create(
                user=request.user,
                task_instance=task_instance,
                text=text
            )
            comment.save()
            messages.success(request, 'Comment successfully added.')
        else:
            messages.error(request, 'Comment text cannot be empty.')

        return redirect('feed:task_detail', task_instance_id)

    def get(self, request, *args, **kwargs):
        return redirect('feed:index')