# Generated by Django 4.1.7 on 2023-02-16 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendrequest',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='friendrequest',
            name='from_user',
        ),
        migrations.RemoveField(
            model_name='friendrequest',
            name='to_user',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Friend',
        ),
        migrations.DeleteModel(
            name='FriendRequest',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
