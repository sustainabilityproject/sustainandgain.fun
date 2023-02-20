from django.contrib import admin
from .models import Task, TaskCategory

admin.site.register(Task)
admin.site.register(TaskCategory)

# Register your models here.
