from django.test import TestCase
from ..factories.tasks_factory import TaskCategoryFactory, TaskFactory, TaskInstanceFactory
from tasks.models import *
from friends.models import Profile
from django.contrib.auth.models import User
from datetime import timedelta


class TaskTestCase(TestCase):

    def test_negative_points(self):
        task = TaskFactory.build()
        task.points = -5
        self.assertRaises(ValidationError, task.clean)

    def test_zero_points(self):
        task = TaskFactory.build()
        task.points = 0
        self.assertRaises(ValidationError, task.clean)

    def test_negative_repeat_time(self):
        task = TaskFactory.build()
        task.time_to_repeat = timedelta(-999)
        self.assertRaises(ValidationError, task.clean)