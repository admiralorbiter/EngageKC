from datetime import timedelta
from django.utils import timezone  # Change this import
from django.core.exceptions import ValidationError  # Change this import
from django.db.utils import IntegrityError  # Add this import
from django.forms import ValidationError
from django.test import TestCase
from django.core.management import call_command
from video_app.models import Session, Media, CustomAdmin, Student

class BaseTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        call_command('loaddata', 'initial_data.json', verbosity=0)
        self.admin = CustomAdmin.objects.create_user(username='testadmin', password='testpass')

class SessionTestCase(BaseTestCase):
    def test_duplicate_session_code(self):
        # Create a session with a specific session_code
        session1 = Session.objects.create(
            name="Test Session 1",
            section=1,
            created_by=self.admin
        )

        # Attempt to create another session with the same session_code
        with self.assertRaises(ValidationError):
            Session.objects.create(
                name="Test Session 2",
                section=2,
                created_by=self.admin,
                session_code=session1.session_code
            )

    def test_session_code_length(self):
        # Attempt to create a session with a session_code that's too long
        with self.assertRaises(ValidationError):
            session = Session(
                name="Test Session",
                section=1,
                created_by=self.admin,
                session_code="ABCDEFGHI"  # 9 characters, should be max 8
            )
            session.full_clean()

    def test_negative_section_number(self):
        # Attempt to create a session with a negative section number
        with self.assertRaises(ValidationError):
            session = Session(
                name="Test Session",
                section=-1,
                created_by=self.admin
            )
            session.full_clean()

    def test_very_long_session_name(self):
        # Attempt to create a session with a very long name
        with self.assertRaises(ValidationError):
            session = Session(
                name="A" * 101,  # 101 characters, should be max 100
                section=1,
                created_by=self.admin
            )
            session.full_clean()

    def test_session_without_created_by(self):
        # Create a session without a created_by user
        session = Session.objects.create(
            name="Orphan Session",
            section=1
        )
        self.assertIsNone(session.created_by)

    def test_delete_admin_user(self):
        # Create a session with an admin user
        session = Session.objects.create(
            name="Admin's Session",
            section=1,
            created_by=self.admin
        )

        # Delete the admin user
        self.admin.delete()

        # Refresh the session from the database
        session.refresh_from_db()

        # Check that the session still exists but has no created_by user
        self.assertIsNone(session.created_by)

    def test_student_association(self):
        # Create a session
        session = Session.objects.create(
            name="Student's Session",
            section=1,
            created_by=self.admin
        )

        # Create a student associated with the session
        student = Student.objects.create(
            name="Test Student",
            password="testpass",
            section=session,
            admin=self.admin
        )

        # Check that the student is correctly associated with the session
        self.assertEqual(session.students.count(), 1)
        self.assertEqual(session.students.first(), student)

        # Delete the session
        session.delete()

        # Check that the student was also deleted (due to CASCADE)
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(pk=student.pk)

    def test_days_until_deletion(self):
        # Test for paused session
        paused_session = Session.objects.create(
            name="Paused Session",
            section=1,
            is_paused=True,
            created_by=self.admin
        )
        self.assertEqual(paused_session.days_until_deletion(), 'Paused')

        # Test for session created today
        today_session = Session.objects.create(
            name="Today's Session",
            section=2,
            created_by=self.admin
        )
        self.assertEqual(today_session.days_until_deletion(), 360)

        # Test for session created 30 days ago
        month_old_session = Session.objects.create(
            name="Month Old Session",
            section=3,
            created_by=self.admin
        )
        month_old_session.created_at = timezone.now() - timedelta(days=30)
        month_old_session.save()
        self.assertEqual(month_old_session.days_until_deletion(), 330)

        # Test for session created 359 days ago
        almost_expired_session = Session.objects.create(
            name="Almost Expired Session",
            section=4,
            created_by=self.admin
        )
        almost_expired_session.created_at = timezone.now() - timedelta(days=359)
        almost_expired_session.save()
        self.assertEqual(almost_expired_session.days_until_deletion(), 1)

        # Test for session created 360 days ago
        expired_session = Session.objects.create(
            name="Expired Session",
            section=5,
            created_by=self.admin
        )
        expired_session.created_at = timezone.now() - timedelta(days=360)
        expired_session.save()
        self.assertEqual(expired_session.days_until_deletion(), 0)

        # Test for session created more than 360 days ago
        long_expired_session = Session.objects.create(
            name="Long Expired Session",
            section=6,
            created_by=self.admin
        )
        long_expired_session.created_at = timezone.now() - timedelta(days=400)
        long_expired_session.save()
        self.assertEqual(long_expired_session.days_until_deletion(), 0)

    def test_session_expiration_logic(self):
        # Test for paused session
        paused_session = Session.objects.create(
            name="Paused Session",
            section=1,
            is_paused=True,
            created_by=self.admin
        )
        self.assertFalse(paused_session.is_expired())

        # Test for session created less than 7 days ago
        recent_session = Session.objects.create(
            name="Recent Session",
            section=2,
            created_by=self.admin
        )
        self.assertFalse(recent_session.is_expired())

        # Test for session created more than 7 days ago
        old_session = Session.objects.create(
            name="Old Session",
            section=3,
            created_by=self.admin
        )
        # Manually set the created_at date to 8 days ago
        old_session.created_at = timezone.now() - timedelta(days=8)
        old_session.save()
        self.assertTrue(old_session.is_expired())

        # Additional test: Paused session created more than 7 days ago
        old_paused_session = Session.objects.create(
            name="Old Paused Session",
            section=4,
            is_paused=True,
            created_by=self.admin
        )
        old_paused_session.created_at = timezone.now() - timedelta(days=8)
        old_paused_session.save()
        self.assertFalse(old_paused_session.is_expired())

class MediaTestCase(BaseTestCase):
    def test_media_creation(self):
        # Check if media objects were created
        media_count = Media.objects.count()
        self.assertEqual(media_count, 50)  # Assuming there are 50 media objects in the fixture

    def test_media_fields(self):
        # Check fields of a specific media object
        media = Media.objects.first()
        self.assertEqual(media.title, "Test Media 1")
        self.assertEqual(media.description, "This is test media upload 1.")
        self.assertEqual(media.tag, "education")
        self.assertEqual(media.media_type, "image")
        self.assertEqual(media.image_file, "images/test2.png")
        self.assertFalse(bool(media.video_file))
        self.assertEqual(media.graph_likes, 0)
        self.assertEqual(media.eye_likes, 0)
        self.assertEqual(media.read_likes, 0)
        self.assertFalse(media.is_graph)
        self.assertIsNone(media.graph_tag)
        self.assertIsNone(media.variable_tag)
        self.assertIsNone(media.submitted_password)

    def test_session_media_relationship(self):
        # Check if media objects are correctly associated with the session
        session = Session.objects.first()
        session_media_count = session.media.count()
        self.assertEqual(session_media_count, 50)  # Assuming all media belong to the same session

    def test_custom_admin_creation(self):
        # Check if the CustomAdmin user was created
        admin = CustomAdmin.objects.filter(username="admin").first()
        self.assertIsNotNone(admin)
        # Add more assertions for CustomAdmin fields if needed

    # Add more tests as needed
