# video_app/tasks.py

from celery import shared_task
from .models import Session
from django.utils import timezone
from datetime import timedelta

@shared_task
def clear_expired_sessions():
    expired_sessions = Session.objects.filter(is_paused=False, created_at__lte=timezone.now() - timedelta(days=7))
    for session in expired_sessions:
        session.delete()
