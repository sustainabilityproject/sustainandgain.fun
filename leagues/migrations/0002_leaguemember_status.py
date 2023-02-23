# Generated by Django 4.1.7 on 2023-02-23 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguemember',
            name='status',
            field=models.CharField(choices=[('invited', 'Invited'), ('joined', 'Joined'), ('pending', 'Pending')], default='pending', max_length=20),
        ),
    ]
