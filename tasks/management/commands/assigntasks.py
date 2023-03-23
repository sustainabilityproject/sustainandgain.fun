import random

from django.core.management.base import BaseCommand

from friends.models import Profile
from tasks.models import Task, TaskInstance


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

            # filter task instances which are active and have not been completed
            active_tasks = TaskInstance.objects.filter(profile=profile, status=TaskInstance.ACTIVE)
            if len(active_tasks) > 5:
                print(f"Assigned no tasks to user {profile.user.username} since they have more than 5 active tasks "
                      f"({len(active_tasks)}).")

            elif len(active_tasks) == Task.objects.all().count():
                print(f"Assigned no tasks to user {profile.user.username} since they have all tasks active.")

            else:
                random_task = random.choice(Task.objects.all())

                # Check if the random task is available for the user.
                # If not, keep trying until we find one that is available (max 100 tries).
                for i in range(100):
                    if random_task.is_available(profile):
                        break
                    else:
                        random_task = random.choice(Task.objects.all())

                # then create a new instance of that task for them
                if random_task.is_available(profile):
                    t = TaskInstance(
                        task=random_task,
                        profile=profile,
                        status=TaskInstance.ACTIVE,
                        tagged_by='SusSteve',
                        origin_message='Sustainable Steve tagged you!'
                    )
                    t.save()

                    print(f"Assigned task {random_task.title} to user {profile.user.username}")
