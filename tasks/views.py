import base64
import uuid
import autoencoder
import os
from PIL import Image, ImageOps
from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from sustainability.settings import BASE_DIR


def index(request):
    tasks_list = Task.objects.all()
    context = {'tasks_list': tasks_list}
    return render(request, 'tasks/index_bootstrap.html', context)


def my_tasks(request):
    return HttpResponse("Here are the tasks you currently have active!")



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