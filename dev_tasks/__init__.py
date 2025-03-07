from __future__ import absolute_import, unicode_literals

# This will make sure the Celery app is always imported when
# Django starts, so tasks can be discovered automatically.
from .celery import app as celery_app

__all__ = ("celery_app",)
