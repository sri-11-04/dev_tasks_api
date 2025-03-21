# Generated by Django 5.1.6 on 2025-02-25 04:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_remove_tasks_assigned_to_tasks_due_date_tasks_team_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasks',
            name='team',
        ),
        migrations.AddField(
            model_name='taskassignment',
            name='is_in_team',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='tasks',
            name='project_teams',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.projectteams'),
        ),
    ]
