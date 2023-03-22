from accounts.models import User
from friends.models import Profile
from leagues.models import League
from tasks.models import Task, TaskInstance

# operations = [
#     migrations.CreateModel(
#         name='User',
#         fields=[
#             ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#             ('password', models.CharField(max_length=128, verbose_name='password')),
#             ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
#             ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
#             ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
#             ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
#             ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
#             ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
#             ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
#             ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
#             ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
#             ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
#             ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
#         ],
#         options={
#             'verbose_name': 'user',
#             'verbose_name_plural': 'users',
#             'abstract': False,
#         },
#         managers=[
#             ('objects', django.contrib.auth.models.UserManager()),
#         ],
#     ),
# ]

class Command(BaseCommand):
    help = 'Create the account and league for sustainability steve'

    def handle(self, *args, **options):
        user = User.objects.create_user(
            username='sustainabilitysteve',
            email='sustainabilitysteve@localhost',
            password='sustainabilitysteve',
            first_name='Sustainability',
            last_name='Steve',
        )

        profile = Profile.objects.create(
            user=user,
            bio='I am Sustainability Steve. I am here to help you be more sustainable.',
            avatar='media/default/sussteve.png',
        )