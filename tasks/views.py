# TODO class rather than function views
from .models import *
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class MyTasksView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/mytasks.html"

    def get_context_data(self, **kwargs):
        current_user = self.request.user
        user_tasks = TaskInstance.objects.filter(user=current_user)

        context = super().get_context_data(**kwargs)
        context['current_user'] = current_user
        context['user_tasks'] = user_tasks

        return context


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate a list of all tasks that are available for this user
        current_user = self.request.user
        tasks_list = [task for task in Task.objects.all() if task.is_available(current_user)]
        context['tasks_list'] = tasks_list
        return context


@login_required
def accept_task(request, task_id):
    """When the user accepts a task, create a new active TaskInstance referencing that user and the accepted task"""
    task_accepted = Task.objects.get(pk=task_id)

    if task_accepted.is_available(request.user):
        t = TaskInstance(
            task=task_accepted,
            user=request.user,
            status=TaskInstance.ACTIVE
        )
        t.save()

    return redirect('my_tasks')
