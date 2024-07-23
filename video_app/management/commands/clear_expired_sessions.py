from django.core.management.base import BaseCommand
from video_app.models import Session
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes expired sessions'

    def handle(self, *args, **kwargs):
        expired_sessions = Session.objects.filter(is_paused=False, created_at__lte=timezone.now() - timedelta(days=7))
        for session in expired_sessions:
            session.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted session {session.id}'))
