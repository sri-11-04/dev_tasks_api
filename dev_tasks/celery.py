from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_tasks.settings")

app = Celery("dev_tasks")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
