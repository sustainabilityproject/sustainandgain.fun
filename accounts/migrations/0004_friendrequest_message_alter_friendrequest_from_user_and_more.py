# Generated by Django 4.1.6 on 2023-02-15 20:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0003_friendrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="friendrequest",
            name="message",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="friendrequest",
            name="from_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="friend_requests_sent",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="friendrequest",
            name="to_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="friend_requests_received",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="friendrequest",
            unique_together={("from_user", "to_user")},
        ),
    ]
