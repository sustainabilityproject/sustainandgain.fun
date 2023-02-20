# Generated by Django 4.1.7 on 2023-02-16 23:30

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('points', models.IntegerField(default=0)),
                ('time_to_repeat', models.DurationField(verbose_name=datetime.timedelta(days=1))),
            ],
        ),
        migrations.CreateModel(
            name='TaskCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='TaskInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_accepted', models.DateTimeField(auto_now_add=True)),
                ('time_completed', models.DateTimeField(default=None)),
                ('status', models.CharField(choices=[('COMPLETED', 'Completed'), ('PENDING', 'Pending'), ('ACTIVE', 'Active')], default='ACTIVE', max_length=9)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tasks.task')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tasks.taskcategory'),
        ),
    ]
