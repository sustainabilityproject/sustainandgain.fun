from django.core.management.base import BaseCommand, CommandError
from accounts.models import User
from friends.models import Profile
from leagues.models import League
from tasks.models import Task, TaskInstance, TaskCategory

import random
import datetime

class Command(BaseCommand):
    help = 'Create the account and league for sustainability steve'

    def handle(self, *args, **options):
        # if alice does not exist
        if not User.objects.filter(username='SusSteve').exists():
            user = User.objects.create_user(
                username='SusSteve',
                email='sustainabilitysteve@localhost',
                password="".join(random.choice(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")) for i in range(20)),
                first_name='Sustainability',
                last_name='Steve',
            )

            league = League.objects.create(
                name='Steve\'s League',
                description='Leagues are a great way to compete against friends and see who can earn the most points by completing tasks and making sustainable choices. To use the league, all you have to do is complete tasks. Your points will be automatically added to the leaderboard, where you can see how you stack up against other users. But that\'s not all - you can also create and manage your own leagues. Invite your friends, family, or colleagues to join and see who can make the biggest impact on the environment!',
                visibility='public',
                invite_only=False,
            )

            # Find the profile with the same user as the user we just created
            profile = Profile.objects.get(user=user)

            league.members.add(profile)
            league.add_admin(profile)

            daily_category = TaskCategory.objects.create(
                category_name='Daily',
            )

            commuting = Task.objects.create(
                title='Non-polluting commuting',
                description='Hey everyone, it\'s Sustainability Steve here! Today, I cycled to campus instead of driving. Not only did I get some exercise, but I also reduced my carbon footprint and helped reduce traffic congestion around campus. On this feed, you can view all of your friends\' submitted tasks, check out the friends page to send some invitations! Don\'t forget, you can complete your own tasks by heading over to the tasks page. Let\'s keep up the great work!',
                points=50,
                time_to_repeat=datetime.timedelta(days=1),
                category=daily_category,
                rarity=0,
                is_bomb=False,
                can_user_self_assign=False,
            )

            time = datetime.datetime.now(tz=datetime.timezone.utc)

            TaskInstance.objects.create(
                task=commuting,
                profile=profile,
                time_accepted=time,
                time_completed=time,
                status='complete',
                photo='default/stevebike.png',
            )