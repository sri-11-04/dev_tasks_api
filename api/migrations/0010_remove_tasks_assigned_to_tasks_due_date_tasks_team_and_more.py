# Generated by Django 5.1.6 on 2025-02-24 12:25

import api.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_projectteams_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasks',
            name='assigned_to',
        ),
        migrations.AddField(
            model_name='tasks',
            name='due_date',
            field=models.DateField(default=api.models.default_time),
        ),
        migrations.AddField(
            model_name='tasks',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='api.team'),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='api.projects'),
        ),
        migrations.CreateModel(
            name='TaskAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='api.tasks')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_assignments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
