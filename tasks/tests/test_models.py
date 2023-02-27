from django.test import TestCase
from tasks.tests.factories import TaskFactory, TaskInstanceFactory
from friends.tests.factories import ProfileFactory
from tasks.models import *
from datetime import timedelta


class TaskInvalidValues(TestCase):

    def test_negative_points(self):
        task = TaskFactory.build(
            points=-5
        )
        self.assertRaises(ValidationError, task.clean)

    def test_zero_points(self):
        task = TaskFactory.build(
            points=0
        )
        self.assertRaises(ValidationError, task.clean)

    def test_negative_repeat_time(self):
        task = TaskFactory.build(
            time_to_repeat=timedelta(-999)
        )

        self.assertRaises(ValidationError, task.clean)


class TaskAvailability(TestCase):

    @classmethod
    def setUpTestData(cls):
        for title in ["A", "B", "C"]:
            TaskFactory.create(title=title)

    def test_tasks_are_available(self):
        """Verify that tasks with no instances for a user are available to that user."""
        profile = ProfileFactory.create()
        tasks = Task.objects.all()

        # Assert that there are three tasks in the database and they are all available to the user
        self.assertEqual(len(tasks), 3)
        for task in tasks:
            self.assertTrue(
                task.is_available(profile)
            )

    def test_active_tasks_are_unavailable(self):
        """Verify that tasks with active instances are unavailable to that user."""
        profile = ProfileFactory.create()

        task_A = Task.objects.get(title="A")
        task_B = Task.objects.get(title="B")
        task_C = Task.objects.get(title="C")

        # Generate an instance of Task "A" for the user
        TaskInstanceFactory.create(
            task=task_A,
            profile=profile
        )

        # Assert that Task "A" is unavailable for the user, while Tasks "B" and "C" are
        available_tasks = [t for t in Task.objects.all() if t.is_available(profile)]
        self.assertNotIn(task_A, available_tasks)
        self.assertIn(task_B, available_tasks)
        self.assertIn(task_C, available_tasks)


class TaskInstanceInvalidValues(TestCase):
    def test_time_complete_status_active(self):
        instance = TaskInstanceFactory.build()
        self.assertEqual(instance.status, TaskInstance.ACTIVE)

        instance.time_completed = timezone.now()
        self.assertRaises(ValidationError, instance.clean)

    def test_no_time_complete_status_pending(self):
        instance = TaskInstanceFactory.build()
        self.assertIsNone(instance.time_completed)

        instance.status = TaskInstance.PENDING_APPROVAL
        self.assertRaises(ValidationError, instance.clean)

    def test_no_time_complete_status_completed(self):
        instance = TaskInstanceFactory.build()
        self.assertIsNone(instance.time_completed)

        instance.status = TaskInstance.COMPLETED
        self.assertRaises(ValidationError, instance.clean)

    def test_time_complete_after_time_accepted(self):
        instance = TaskInstanceFactory.build()
        self.assertLess(instance.time_accepted, timezone.now())

        instance.time_completed = timezone.now() + datetime.timedelta(hours=1)
        self.assertRaises(ValidationError, instance.clean)
