# Generated by Django 4.1.7 on 2023-02-23 14:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_alter_task_time_to_repeat_alter_taskinstance_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskcategory',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterField(
            model_name='task',
            name='time_to_repeat',
            field=models.DurationField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
