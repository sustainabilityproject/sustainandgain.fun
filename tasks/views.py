# TODO class rather than function views
import base64
import uuid
import autoencoder
import os
from PIL import Image, ImageOps
import base64
import uuid
import autoencoder
import os
from PIL import Image, ImageOps
from django.shortcuts import render
from .models import *
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from sustainability.settings import BASE_DIR
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from sustainability.settings import BASE_DIR


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