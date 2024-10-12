from django.test import TestCase
from django.utils import timezone
from video_app.models import Session, CustomAdmin

class SessionModelTest(TestCase):
    def setUp(self):
        self.admin = CustomAdmin.objects.create_user(
            username='testadmin',
            password='testpass',
            school='Test School',
            district='Test District'
        )

    def test_session_creation(self):
        session = Session.objects.create(
            name="Test Session",
            section=1,
            created_by=self.admin
        )
        
        self.assertEqual(session.name, "Test Session")
        self.assertEqual(session.section, 1)
        self.assertEqual(session.created_by, self.admin)
        self.assertIsNotNone(session.session_code)
        self.assertFalse(session.is_paused)
        self.assertIsNotNone(session.created_at)
        self.assertLess((timezone.now() - session.created_at).total_seconds(), 1)