# Generated by Django 5.1.6 on 2025-02-25 12:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_remove_tasks_team_taskassignment_is_in_team_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskassignment',
            name='task',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.tasks'),
        ),
    ]
