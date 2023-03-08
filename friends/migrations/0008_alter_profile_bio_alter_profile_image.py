# Generated by Django 4.1.7 on 2023-03-01 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0007_alter_profile_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default/default.jpg', upload_to='profile_pics'),
        ),
    ]
