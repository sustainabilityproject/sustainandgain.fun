# TODO proper code comments and documentation
import datetime

from accounts.models import User
from django.db import models


class TaskCategory(models.Model):
    category_name = models.CharField(max_length=30)

    def __str__(self):
        return self.category_name

    # Ensures the plural of category is correctly 'categories' in the admin page
    # (otherwise Django thinks it is 'categorys')
    class Meta:
        verbose_name_plural = "categories"


class Task(models.Model):
    """Tasks are created and maintained by Gamekeepers."""
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    # by default, a task gives no points - this is something Gamekeepers have to implement
    points = models.IntegerField(default=0)

    # by default, tasks can be repeated after a day
    time_to_repeat = models.DurationField()

    # PROTECT means that a category cannot be deleted while tasks exist under that category
    category = models.ForeignKey(TaskCategory, on_delete=models.PROTECT)

    def is_available(self, user):
        """
        Check if this task should be available for a given user.
        If the user has ACTIVE or PENDING_APPROVAL instances of this task, or the time_to_repeat has not elapsed since
        the user completed an instance of this task, return false. Otherwise, return true.
        """
        this_task_instances = TaskInstance.objects.filter(task=self.pk, user=user)

        for instance in this_task_instances:
            if instance.status in [TaskInstance.PENDING_APPROVAL, TaskInstance.ACTIVE]:
                return False

            else:
                if datetime.now() < instance.time_completed + instance.time_to_repeat:
                    return False

        return True

    def __str__(self):
        return self.title


class TaskInstance(models.Model):
    """
    TaskInstance represents a specific instance of a task, undertaken by a user.
    They are generated when a user selects a Task to complete.
    """

    # This references the task the user has accepted
    task = models.ForeignKey(Task, on_delete=models.PROTECT)

    # The datetime that the user accepted the task - important for timed tasks
    # Set this to the time that TaskInstance is instantiated
    time_accepted = models.DateTimeField(auto_now_add=True)

    time_completed = models.DateTimeField(null=True, blank=True)

    # The user who has accepted the task
    # TODO make sure this is consistent with the user profile system
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Constants representing possible task states
    COMPLETED = 'COMPLETED'
    PENDING_APPROVAL = 'PENDING'
    ACTIVE = 'ACTIVE'

    TASK_STATE_CHOICES = (
        (COMPLETED, 'Completed'),
        (PENDING_APPROVAL, 'Pending'),
        (ACTIVE, 'Active'),
    )
    status = models.CharField(
        max_length=9,
        choices=TASK_STATE_CHOICES,
        default=ACTIVE,
    )

    # When the task has been validated as completed (e.g. by a Gamekeeper, or automatically for simple tasks)
    def validate_task(self):
        # TODO add more complex validation from Gamekeepers
        self.status = self.COMPLETED

    # When the user reports themself as having completed a task
    def report_task_complete(self):
        self.status = self.PENDING_APPROVAL
        self.time_completed = datetime.now()

    def __str__(self):
        return f"Task:{self.task.title}; User:{self.user.username}"
