import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from friends.models import Profile


class TaskCategory(models.Model):
    """Categories are created and maintained by Gamekeepers."""
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
    time_to_repeat = models.DurationField(default=datetime.timedelta(days=1))

    # PROTECT means that a category cannot be deleted while tasks exist under that category
    category = models.ForeignKey(TaskCategory, on_delete=models.PROTECT)

    # TODO rarity as an attribute of Task? possibly limit task instances to a percentage of users
    GOLD = 3
    SILVER = 2
    NORMAL = 1
    TASK_RARITY_CHOICES = (
        (1, "Normal"),
        (2, "Silver"),
        (3, "Gold")
    )

    @property
    def rarity_colour(self):
        if self.rarity == self.GOLD:
            return "badge-gold"

        elif self.rarity == self.SILVER:
            return "badge-silver"

    rarity = models.IntegerField(choices=TASK_RARITY_CHOICES, default=1)



    def is_available(self, profile):
        """
        Check if this task should be available for a given user.
        If the user has ACTIVE or PENDING_APPROVAL instances of this task, or the time_to_repeat has not elapsed since
        the user completed an instance of this task, return false. Otherwise, return true.
        """
        this_task_instances = TaskInstance.objects.filter(task=self.pk, profile=profile.pk)

        for instance in this_task_instances:
            if instance.status in [TaskInstance.PENDING_APPROVAL, TaskInstance.ACTIVE]:
                return False

            else:
                if timezone.now() < instance.time_completed + instance.task.time_to_repeat:
                    return False

        return True

    def clean(self):
        time_to_repeat = self.time_to_repeat
        if time_to_repeat < datetime.timedelta(0):
            raise ValidationError('Time to repeat cannot be negative')

        if self.points <= 0:
            raise ValidationError('Tasks must grant a positive number of points')

        return self

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

    # Photo evidence of the task being completed
    photo = models.ImageField(upload_to='task_photos', null=True, blank=True)

    # Completion note
    note = models.CharField(max_length=500, null=True, blank=True)

    # The profile of the user who has accepted the task
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)

    # The profiles of the users who have liked the task, users can only like one post once
    likes = models.ManyToManyField(Profile, related_name='likes', blank=True)

    # The profiles of the users who have reported the task, users can only report one post once
    reports = models.ManyToManyField(Profile, related_name='reports', blank=True)

    # The location of where the task was completed
    location = models.CharField(max_length=500, null=True, blank=True)

    # Shows in the MyTasks view, lets you know who tagged you
    origin_message = models.CharField(max_length=50, default='This task is available')

    # TODO record whether you've tagged someone in this task already -- literally just a Boolean
    tagged_someone = models.BooleanField(default=False)

    # Constants representing possible task states
    COMPLETED = 'COMPLETED'
    PENDING_APPROVAL = 'PENDING'
    ACTIVE = 'ACTIVE'

    TASK_STATE_CHOICES = (
        (COMPLETED, 'Completed'),
        (PENDING_APPROVAL, 'Pending Approval'),
        (ACTIVE, 'Active'),
    )
    status = models.CharField(
        max_length=9,
        choices=TASK_STATE_CHOICES,
        default=ACTIVE,
    )

    def __str__(self):
        return f"Task:{self.task.title}; User:{self.profile.user.username}"

    # Returns the colour of the status badge of the task
    @property
    def status_colour(self):
        if self.status == TaskInstance.ACTIVE:
            return 'bg-primary'
        elif self.status == TaskInstance.PENDING_APPROVAL:
            return 'bg-warning text-dark'
        elif self.status == TaskInstance.COMPLETED:
            return 'text-bg-success'


    def clean(self):
        time_completed = self.time_completed
        time_accepted = self.time_accepted
        status = self.status

        if time_completed is not None:
            if time_completed < time_accepted:
                raise ValidationError("Tasks cannot have been completed before they were accepted.")
            if time_completed > timezone.now():
                raise ValidationError("Tasks cannot have been completed in the future.")

        # Validate that there is only a time_completed when the task is Completed or Pending, and vice versa
        if status == TaskInstance.ACTIVE and time_completed is not None:
            raise ValidationError("Tasks cannot have a time completed while they are active.")
        elif status != TaskInstance.ACTIVE and time_completed is None:
            raise ValidationError("If a task is no longer active, it must have a time completed")

        return self

    # When the user reports themselves as having completed a task
    def report_task_complete(self):
        self.status = self.PENDING_APPROVAL
        self.time_completed = timezone.now()
