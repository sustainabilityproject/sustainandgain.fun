from django.test import TestCase
from tasks.models import *
from datetime import timedelta


# Create your tests here.

class TaskTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = TaskCategory.objects.create(category_name="Test Tasks")

    def setUp(self):
        test_task = Task.objects.create(
            title="Test Task",
            description="description",
            points=10,
            time_to_repeat=timedelta(days=1),
            category=TaskCategory.objects.get(category_name="Test Tasks")
        )

    def test_negative_points(self):
        task = Task.objects.get(title="Test Task")
        task.points = -5
        self.assertRaises(ValidationError, task.clean)

    def test_zero_points(self):
        task = Task.objects.get(title="Test Task")
        task.points = 0
        self.assertRaises(ValidationError, task.clean)

    def test_negative_repeat_time(self):
        task = Task.objects.get(title="Test Task")
        task.time_to_repeat = timedelta(-999)
        self.assertRaises(ValidationError, task.clean)


