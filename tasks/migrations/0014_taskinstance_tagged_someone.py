# Generated by Django 4.1.7 on 2023-03-08 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_merge_20230301_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskinstance',
            name='tagged_someone',
            field=models.BooleanField(default=False),
        ),
    ]