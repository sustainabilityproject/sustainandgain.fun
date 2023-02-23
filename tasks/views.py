# TODO class rather than function views
import base64
import os
import uuid

import autoencoder
from PIL import Image, ImageOps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView

from sustainability.settings import BASE_DIR
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
        return TaskInstance.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.ACTIVE]
        context['completed_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.COMPLETED]
        context['pending_tasks'] = [task for task in context['tasks'] if task.status == TaskInstance.PENDING_APPROVAL]
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    """
    List of all tasks that are available for the current user.
    """
    template_name = "tasks/available_tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate a list of all tasks that are available for this user
        current_user = self.request.user
        tasks_list = [task for task in Task.objects.all() if task.is_available(current_user)]
        context['tasks_list'] = tasks_list
        return context


# @login_required
# def accept_task(request, task_id):
#     """When the user accepts a task, create a new active TaskInstance referencing that user and the accepted task"""
#     task_accepted = Task.objects.get(pk=task_id)
#
#     if task_accepted.is_available(request.user):
#         t = TaskInstance(
#             task=task_accepted,
#             user=request.user,
#             status=TaskInstance.ACTIVE
#         )
#         t.save()
#
#     return redirect('tasks:list')

class AcceptTaskView(LoginRequiredMixin, View):
    """
    When the user accepts a task, create a new active TaskInstance referencing that user and the accepted task
    """
    def get(self, request, *args, **kwargs):
        task_accepted = Task.objects.get(pk=self.kwargs['pk'])
        if task_accepted.is_available(request.user):
            t = TaskInstance(
                task=task_accepted,
                user=request.user,
                status=TaskInstance.ACTIVE
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
        if task.user != request.user:
            return redirect('my_tasks')
        # Redirect if the task is already completed
        if task.status == TaskInstance.COMPLETED:
            return redirect('my_tasks')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return TaskInstance.objects.get(pk=self.kwargs['pk'])


class TakePhotoView(TemplateView):
    template_name = 'tasks/take_photo.html'

    def post(self, request):
        image_data = request.POST.get('image_data')
        img_data = base64.b64decode(image_data.split(',')[1])
        image_name = f'{uuid.uuid4()}.png'
        with open(os.path.join(BASE_DIR, "media", image_name), 'wb') as f:
            f.write(img_data)

        with Image.open(os.path.join(BASE_DIR, "media", image_name), 'r') as img:
            # get dimensions of image
            width, height = img.size

            # calculate coordinates for cropping
            left = (width - min(width, height)) // 2
            upper = (height - min(width, height)) // 2
            right = left + min(width, height)
            lower = upper + min(width, height)

            # crop the image
            img = img.crop((left, upper, right, lower))

            # resize the image to 64x64
            img = img.resize((32, 32))

            # fix orientation metadata using ImageOps.exif_transpose()
            img = ImageOps.exif_transpose(img)

            # save the cropped and resized image
            img.save(os.path.join(BASE_DIR, "media", image_name))
        confidence = autoencoder.mug_confidence(os.path.join(BASE_DIR, "media", image_name))

        if os.path.exists(os.path.join(BASE_DIR, "media", image_name)):
            os.remove(os.path.join(BASE_DIR, "media", image_name))
        else:
            print("Failed to delete file")
        print(f"My reconstruction loss: {confidence}")
        if confidence < 0.03:
            return redirect('friends:list')
        else:
            return redirect('friends:profile')
