import random

from django.core.management.base import BaseCommand, CommandError
from tasks.models import Task, TaskInstance
from friends.models import Profile
from notifications.signals import notify


class Command(BaseCommand):
    """
    A command that can be run from the console via manage.py to assign a valid task to each user.

    Attributes:
        help:   The help message given by the console for this command

    Methods:
        handle(self):   The code run by calling this command
    """
    help = 'Assigns a valid task to each user'

    def handle(self, *args, **options):
        """
        The code run by calling this command.

        Iterates through all users and assigns users with less than five active tasks a new task from Sustainable Steve
        """

        for profile in Profile.objects.all():

            if profile.taskinstance_set.count() >= 5:
                print(f"Assigned no tasks to user {profile.user.username} since they have more than 5 active tasks "
                      f"({profile.taskinstance_set.count()}).")

            elif profile.taskinstance_set.count() == Task.objects.all().count():
                print(f"Assigned no tasks to user {profile.user.username} since they have all tasks active.")

            else:
                random_task = random.choice(Task.objects.all())

                # keep picking tasks until we get one available for the user
                while not random_task.is_available(profile):
                    random_task = random.choice(Task.objects.all())

                # then create a new instance of that task for them
                if random_task.is_available(profile):
                    t = TaskInstance(
                        task=random_task,
                        profile=profile,
                        status=TaskInstance.ACTIVE,
                        origin_message='Sustainable Steve tagged you with this task!'
                    )
                    t.save()

                    print(f"Assigned task {random_task.title} to user {profile.user.username}")
