# Use factory_boy library to define default test objects, making tests easier to write and quicker to read

import tasks.models
import factory

class TaskCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = tasks.models.TaskCategory

    category_name = "Test Category"


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = tasks.models.Task
        # django_get_or_create = ('title',)

    title = "Test Task"
    description = "Details about the task"
    points = 10
    category = factory.SubFactory(TaskCategoryFactory)

class TaskInstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = tasks.models.TaskInstance

    task = factory.SubFactory(TaskFactory)


