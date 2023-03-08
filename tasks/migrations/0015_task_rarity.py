# Generated by Django 4.1.7 on 2023-03-08 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_taskinstance_tagged_someone'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='rarity',
            field=models.IntegerField(choices=[(1, 'Normal'), (2, 'Silver'), (3, 'Gold')], default=1, max_length=1),
        ),
    ]