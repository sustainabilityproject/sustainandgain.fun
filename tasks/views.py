# TODO class rather than function views
from .models import *
from django.views.generic import TemplateView


class MyTasksView(TemplateView):
    template_name = "tasks/mytasks.html"

    def get_context_data(self, **kwargs):
        current_user = self.request.user
        user_tasks = TaskInstance.objects.filter(user=current_user)

        context = super().get_context_data(**kwargs)
        context['current_user'] = current_user
        context['user_tasks'] = user_tasks

        return context


class IndexView(TemplateView):
    template_name = "tasks/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks_list'] = Task.objects.all()
        return context

