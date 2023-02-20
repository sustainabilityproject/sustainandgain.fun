from django.shortcuts import render
from .models import *
from django.http import HttpResponse


def index(request):
    tasks_list = Task.objects.all()
    context = {'tasks_list': tasks_list}
    return render(request, 'tasks/index_bootstrap.html', context)


def my_tasks(request):
    return HttpResponse("Here are the tasks you currently have active!")
