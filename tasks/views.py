# TODO class rather than function views

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
    View all the task assigned to the current user.
    """
    model = TaskInstance
    template_name = "tasks/my_tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return TaskInstance.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.ACTIVE]
        context['completed_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.COMPLETED]
        context['pending_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.PENDING_APPROVAL]
        context['friends'] = self.request.user.profile.get_friends()
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    """
    List of all tasks that are available for the current user.
    """
    template_name = "tasks/available_tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate a list of all tasks that are available for this user
        current_profile = self.request.user.profile
        tasks_list = [task for task in Task.objects.all() if task.is_available(current_profile)]
        context['tasks_list'] = tasks_list
        return context


class AcceptTaskView(LoginRequiredMixin, View):
    """
    When the user accepts a task, create a new active TaskInstance referencing that user and the accepted task
    """

    def get(self, request, *args, **kwargs):
        task_accepted = Task.objects.get(pk=self.kwargs['pk'])
        if task_accepted.is_available(request.user.profile):
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
    User can complete a task by uploading a photo of the completed task and has the option to add a note.
    """
    template_name = 'tasks/complete_task.html'
    form_class = CompleteTaskForm
    success_url = reverse_lazy('tasks:list')
    context_object_name = 'task'

    def dispatch(self, request, *args, **kwargs):
        task = TaskInstance.objects.get(pk=self.kwargs['pk'])
        # Redirect if the user is not the owner of the task
        if task.profile != request.user.profile:
            return redirect('my_tasks')
        # Redirect if the task is already completed
        if task.status == TaskInstance.COMPLETED:
            return redirect('my_tasks')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return TaskInstance.objects.get(pk=self.kwargs['pk'])


class SendTagView(LoginRequiredMixin, View):
    """
    Gives your chosen friend the task
    This is very early lol, I'll keep making it
    TODO tag requests rather than forcing tasks
    TODO you can only tag once per task completion
    """
    def post(self, request, *args, **kwargs):
        """
        Puts the task on your friend's profile if it's available to them
        """
        # get the friend's profile
        profile = get_object_or_404(Profile, user__username=request.POST['username'])

        # get the task
        task_sent = Task.objects.get(pk=self.kwargs['pk'])

        # if they don't already have the task, give it to them (not final version)
        if task_sent.is_available(profile.user.profile):
            message = 'Tagged ' + profile.user.username + ' in ' + task_sent.title
            messages.success(request, message)
            t = TaskInstance(
                task=task_sent,
                profile=profile.user.profile,
                status=TaskInstance.ACTIVE,
                origin_message=self.request.user.username + ' tagged you!'
            )
            t.save()
        else:
            message = profile.user.username + ' is already doing that task'
            messages.info(request, message)

        return redirect('tasks:list')
