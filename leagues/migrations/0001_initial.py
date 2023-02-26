# Generated by Django 4.1.7 on 2023-02-23 21:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('friends', '0004_alter_friendrequest_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, default='', max_length=500)),
                ('invite_only', models.BooleanField(default=False)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default='public', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='LeagueMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('member', 'Member'), ('admin', 'Admin')], default='member', max_length=20)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.league')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='friends.profile')),
            ],
        ),
        migrations.AddField(
            model_name='league',
            name='members',
            field=models.ManyToManyField(through='leagues.LeagueMember', to='friends.profile'),
        ),
    ]