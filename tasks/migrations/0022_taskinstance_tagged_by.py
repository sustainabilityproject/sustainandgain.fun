# Generated by Django 4.1.7 on 2023-03-23 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0021_task_can_user_self_assign'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskinstance',
            name='tagged_by',
            field=models.CharField(blank=True, default=None, max_length=150, null=True),
        ),
    ]