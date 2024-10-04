from django.test import TestCase
from django.core.management import call_command
from video_app.models import Session, Media, CustomAdmin

class MediaTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        # Load the fixture data
        call_command('loaddata', 'initial_data.json', verbosity=0)

    def test_session_creation(self):
        # Check if the session was created
        session = Session.objects.first()
        self.assertIsNotNone(session)
        self.assertEqual(session.name, "Test Session")
        self.assertEqual(session.section, 2)
        self.assertEqual(session.session_code, "SEC123")

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
