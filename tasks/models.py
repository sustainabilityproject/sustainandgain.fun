import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from friends.models import Profile


class TaskCategory(models.Model):
    """
    Tasks are sorted into categories e.g. 'transport', 'food', etc.
    Categories are created and maintained by Gamekeepers.

    Attributes:
        category_name (CharField): The name of the category.

    Methods:
        __str__(self): Return str(self).
    """
    category_name = models.CharField(max_length=30)

    def __str__(self):
        return self.category_name

    class Meta:
        """
        Makes the plural of category 'categories' rather than 'categorys' in the admin page
        """
        verbose_name_plural = "categories"


class Task(models.Model):
    """
    Tasks are the foundation of the app.
    Tasks are created and maintained by Gamekeepers.

    Attributes:
        title (CharField): The title of the task.
        description (CharField): The description of the task.
        points (IntegerField): How many points the task is worth.
        time_to_repeat (DurationField): How long it takes for the task to become available again after being completed.
        category (TaskCategory): The category the task belongs to.

    Methods:
        is_available(self, profile): Check if the task is available for the current user.
        clean(self): Raise ValidationError if there are inconsistencies in the time_to_repeat or points.
        __str__(self): Return str(self).
    """
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
        Check if the task is available for the current user.
        Return False if:
            The user has an ACTIVE or PENDING_APPROVAL instance of this task.
            The time_to_repeat has not elapsed since the task instance became COMPLETED.
        Otherwise, return True.

        Args:
            none.

        Returns:
            Boolean: Whether this task is available for the user.
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
        """
        Raise ValidationError if there are inconsistencies in the time_to_repeat or points.

        Args:
            none.

        Returns:
            self (Task): After review.
        """
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
    An instance of a Task belonging to a user.
    They are generated when a user selects a Task to complete or is tagged in one.

    Attributes:
        task (Task): The task of which this is an instance.
        time_accepted (DateTimeField): The time the task was accepted (when this instance was created).
        time_completed (DateTimeField): The time the task was completed.
        photo (ImageField): Photo uploaded by user as proof of completion.
        note (CharField): Comment uploaded by the user when complete.
        profile (Profile): Profile of the instance's owner.
        likes (ManyToManyField(Profile, related_name='likes')): Who has liked the task.
        reports (ManyToManyField(Profile, related_name='likes')): Who has reported the task.
        location (CharField): Where the task was completed.
        origin_message (CharField): Tells user why task is on their 'my tasks' page.
        tagged_someone (BooleanField): Has the user tagged someone else in this task.
        status (CharField): Whether the task is Available, Active, Pending Approval, or Complete.

    Methods:
        __str__(self): Return str(self).
        status_color(self): Return the colour of the task's status badge.
        clean(self): Raise ValidationError if there are inconsistencies in the time_completed and time_accepted.
        report_task_complete(self): The user reports themselves as having completed a task.
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

    # have you tagged someone in this task yet?
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

    @property
    def status_colour(self):
        """
        Return the colour of the task's status badge.

        Args:
            none.

        Returns:
            str: The badge's colour.
        """
        if self.status == TaskInstance.ACTIVE:
            return 'bg-primary'
        elif self.status == TaskInstance.PENDING_APPROVAL:
            return 'bg-warning text-dark'
        elif self.status == TaskInstance.COMPLETED:
            return 'text-bg-success'


    def clean(self):
        """
        Raise ValidationError if there are inconsistencies in the time_completed and time_accepted.
        Tasks must have been completed after they were accepted AND in the past.
        Tasks cannot be active if they have a time completed.
        Tasks must have a time completed if they are not active.

        Args:
            none.

        Returns:
            self (TaskInstance): After review.
        """
        time_completed = self.time_completed
        time_accepted = self.time_accepted
        status = self.status

        # Validate that task was completed in the past and that task was completed after it was accepted
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

    def report_task_complete(self):
        """
        The user reports themselves as having completed a task.
        """
        self.status = self.PENDING_APPROVAL
        self.time_completed = timezone.now()
