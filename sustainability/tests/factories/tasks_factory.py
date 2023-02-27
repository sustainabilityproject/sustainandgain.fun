# Use factory_boy library to define default test objects, making tests easier to write and quicker to read

import tasks.models
import factory
from .friends_factory import ProfileFactory
from django.utils import timezone

class TaskCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = tasks.models.TaskCategory

    category_name = "Test Category"


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = tasks.models.Task

    title = "Test Task"
    description = "Details about the task"
    points = 10
    category = factory.SubFactory(TaskCategoryFactory)

class TaskInstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = tasks.models.TaskInstance

    task = factory.SubFactory(TaskFactory)
    profile = factory.SubFactory(ProfileFactory)
    time_accepted = timezone.now()


