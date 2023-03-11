from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView
from django.contrib import messages

from .forms import CompleteTaskForm
from .models import *


class MyTasksView(LoginRequiredMixin, ListView):
    """
    View all the tasks assigned to the current user, login required.

    Attributes:
        model (TaskInstance): The thing being displayed.
        template_name (str): The html template this view uses.
        context_object_name (str): What this is called in the template.

    Methods:
        get_queryset(self): Return all task instances belonging to current user.
        get_context_data(self, **kwargs): Return user's active, completed, and pending tasks and their friends.
    """
    model = TaskInstance
    template_name = "tasks/my_tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        """
        Return all task instances belonging to current user.

        Returns:
            QuerySet[TaskInstance]: the task instances which belong to the user.
        """
        return TaskInstance.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        """
        Return user's active, completed, and pending tasks and their friends.

        Returns:
            context (dict[str, Any]): active_tasks, completed_tasks, pending_tasks, friends.
        """
        context = super().get_context_data(**kwargs)
        context['active_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.ACTIVE]
        context['completed_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.COMPLETED]
        context['pending_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.PENDING_APPROVAL]
        context['friends'] = self.request.user.profile.get_friends()
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    """
    View of all tasks that are available for the current user, login required.

    Attributes:
        template_name (str): The html template this view uses.

    Methods:
        get_context_data(self, **kwargs): Return tasks which are available for the current user.
    """
    template_name = "tasks/available_tasks.html"

    def get_context_data(self, **kwargs):
        """
        Return tasks which are available for the current user.

        Returns:
            context (dict[str: Any]): tasks_list.
        """
        context = super().get_context_data(**kwargs)

        # Generate a list of all tasks that are available for this user
        current_profile = self.request.user.profile
        tasks_list = [task for task in Task.objects.all() if task.is_available(current_profile)]
        context['tasks_list'] = tasks_list
        return context


class AcceptTaskView(LoginRequiredMixin, View):
    """
    Create new TaskInstance referencing this user and the task they accepted.

    Methods:
        get(self, request, *args, **kwargs): Create task instance for user's 'my tasks' page.
    """

    def get(self, request, *args, **kwargs):
        """
        Create task instance for user's 'my tasks' page.

        Returns:
            redirect: sends you back to tasks:list.
        """
        task_accepted = Task.objects.get(pk=self.kwargs['pk'])
        if task_accepted.is_available(request.user.profile):

            # create new task instance for current profile, set it to active
            t = TaskInstance(
                task=task_accepted,
                profile=request.user.profile,
                status=TaskInstance.ACTIVE,
                origin_message='You accepted this task'
            )
            t.save()
        return redirect('tasks:list')


class CompleteTaskView(LoginRequiredMixin, UpdateView):
    """
    Set task to pending approval when the user has completed it.
    The user can upload a photo and optionally add a note and their location.

    Attributes:
        template_name (str): The html template this view uses.
        form_class (CompleteTaskForm): Form for a user to complete a task.
        success_url (str): Where the form redirects.
        context_object_name (str): What this is called in the template.

    Methods:
        dispatch(self, request, *args, **kwargs): Responsible for request and response.
        get_object(self, queryset=None): Return the object the view is displaying.
    """
    template_name = 'tasks/complete_task.html'
    form_class = CompleteTaskForm
    success_url = reverse_lazy('tasks:list')
    context_object_name = 'task'

    def dispatch(self, request, *args, **kwargs):
        """
        Responsible for request and response.
        Redirects if the user is not the owner of the task or if the task is already completed.
        """
        task = TaskInstance.objects.get(pk=self.kwargs['pk'])
        # Redirect if the user is not the owner of the task
        if task.profile != request.user.profile:
            return redirect('my_tasks')
        # Redirect if the task is already completed
        if task.status == TaskInstance.COMPLETED:
            return redirect('my_tasks')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.

        Returns:
            TaskInstance.
        """
        return TaskInstance.objects.get(pk=self.kwargs['pk'])


class SendTagView(LoginRequiredMixin, View):
    """
    Put selected task on chosen friend's 'my tasks' page, login required.

    Methods:
        post(self, request, *args, **kwargs): Put completed task on tagged friend's 'my tasks' page.
    """
    def post(self, request, *args, **kwargs):
        """
        Put completed task on tagged friend's 'my tasks' page.

        Attributes:
            profile (Profile): The profile of the friend who will receive the task.
            task_instance_sent (TaskInstance): The task instance from which the tag is sent.
            task_sent (Task): The task the friend is being tagged in.

        Returns:
            redirect: sends you back to tasks:list.
        """
        # get the friend's profile
        profile = get_object_or_404(Profile, user__username=request.POST['username'])

        # get the task instance
        task_instance_sent = TaskInstance.objects.get(pk=self.kwargs['pk'])

        # get the task
        task_sent = task_instance_sent.task

        # if they don't already have the task, give it to them
        if task_sent.is_available(profile.user.profile):
            message = 'Tagged ' + profile.user.username + ' in ' + task_sent.title
            messages.success(request, message)

            # create the task instance that goes on the friend's page
            t = TaskInstance(
                task=task_sent,
                profile=profile.user.profile,
                status=TaskInstance.ACTIVE,
                origin_message=self.request.user.username + ' tagged you!'
            )
            t.save()

            # records the person you tagged, you now can't tag anyone else
            task_instance_sent.tagged_someone = True
            task_instance_sent.tagged_whom = profile.user.username
            task_instance_sent.save()
        else:
            message = profile.user.username + ' is already doing that task'
            messages.info(request, message)

        return redirect('tasks:list')
