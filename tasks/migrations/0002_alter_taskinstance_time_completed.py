# Generated by Django 4.1.7 on 2023-02-20 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskinstance',
            name='time_completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
