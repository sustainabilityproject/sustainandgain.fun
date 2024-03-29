# Generated by Django 4.1.7 on 2023-03-13 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0018_taskinstance_tagged_whom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskinstance',
            name='status',
            field=models.CharField(choices=[('COMPLETED', 'Completed'), ('PENDING', 'Pending Approval'), ('ACTIVE', 'Active'), ('EXPLODED', 'Exploded')], default='ACTIVE', max_length=9),
        ),
    ]
