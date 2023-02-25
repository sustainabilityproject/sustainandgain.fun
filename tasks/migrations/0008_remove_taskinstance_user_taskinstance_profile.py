# Generated by Django 4.1.7 on 2023-02-25 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0004_alter_friendrequest_status'),
        ('tasks', '0007_taskinstance_note'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskinstance',
            name='user',
        ),
        migrations.AddField(
            model_name='taskinstance',
            name='profile',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='friends.profile'),
        ),
    ]
