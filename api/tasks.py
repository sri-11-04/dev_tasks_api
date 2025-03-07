from celery import shared_task
from time import sleep
from .models import User,Notification
from django.core.mail import send_mail
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

@shared_task
def sample_notification(email:str)->str:
    sleep(5)
    return f'Notification sent to {email}'

@shared_task
def create_notification(user_id, notification_type, message):
    user = User.objects.get(id=user_id)

    # Save notification in the database
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message
    )

    # Send email notification
    send_mail(
        subject=f"New {notification_type} Notification",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

    logger.info(f"Notification created and email sent to {user.email}")  # Logs in Celery

    return f"Notification created and email sent to {user.email}"  # Also logs the task completion

