from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from video_app.models import Session, CustomAdmin, Media, Student, StudentMediaInteraction, Comment

class SessionModelTest(TestCase):
    def setUp(self):
        self.admin = CustomAdmin.objects.create_user(
            username='testadmin',
            password='testpass',
            school='Test School',
            district='Test District'
        )
        self.session = Session.objects.create(
            name="Test Session",
            section=1,
            created_by=self.admin
        )

    def test_session_creation(self):
        """Test basic session creation and default values"""
        self.assertEqual(self.session.name, "Test Session")
        self.assertEqual(self.session.section, 1)
        self.assertEqual(self.session.created_by, self.admin)
        self.assertIsNotNone(self.session.session_code)
        self.assertEqual(len(self.session.session_code), 8)
        self.assertFalse(self.session.is_paused)
        self.assertEqual(self.session.character_set, 'marvel')

    def test_unique_session_code(self):
        """Test that session codes are unique"""
        session2 = Session.objects.create(
            name="Another Session",
            section=2,
            created_by=self.admin
        )
        self.assertNotEqual(self.session.session_code, session2.session_code)

    def test_negative_section_validation(self):
        """Test validation for negative section numbers"""
        with self.assertRaises(ValidationError):
            session = Session(
                name="Invalid Session",
                section=-1,
                created_by=self.admin
            )
            session.full_clean()

    def test_is_expired_method(self):
        """Test the is_expired method"""
        # Test not expired
        self.assertFalse(self.session.is_expired())

        # Test expired (7 days + 1 minute)
        self.session.created_at = timezone.now() - timedelta(days=7, minutes=1)
        self.session.save()
        self.assertTrue(self.session.is_expired())

        # Test not expired when paused
        self.session.is_paused = True
        self.session.save()
        self.assertFalse(self.session.is_expired())

    def test_days_until_deletion(self):
        """Test the days_until_deletion method"""
        # Test paused session
        self.session.is_paused = True
        self.session.save()
        self.assertEqual(self.session.days_until_deletion(), 'Paused')

        # Test active session
        self.session.is_paused = False
        self.session.save()
        self.assertEqual(self.session.days_until_deletion(), 360)

        # Test old session
        self.session.created_at = timezone.now() - timedelta(days=370)
        self.session.save()
        self.assertEqual(self.session.days_until_deletion(), 0)

    def test_str_method(self):
        """Test the string representation"""
        self.assertEqual(str(self.session), "Test Session")


class MediaModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.admin = CustomAdmin.objects.create_user(
            username='testadmin',
            password='testpass',
            school='Test School',
            district='Test District'
        )
        self.session = Session.objects.create(
            name="Test Session",
            section=1,
            created_by=self.admin
        )
        self.media = Media.objects.create(
            session=self.session,
            title="Test Media",
            description="Test Description",
            media_type='video',
            is_graph=False
        )

    def test_media_creation(self):
        """Test basic media creation and default values"""
        self.assertEqual(self.media.title, "Test Media")
        self.assertEqual(self.media.description, "Test Description")
        self.assertEqual(self.media.media_type, "video")
        self.assertEqual(self.media.graph_likes, 0)
        self.assertEqual(self.media.eye_likes, 0)
        self.assertEqual(self.media.read_likes, 0)
        self.assertFalse(self.media.is_graph)

    def test_media_validation(self):
        """Test media validation rules"""
        # Test video with image file
        with self.assertRaises(ValidationError):
            invalid_media = Media(
                session=self.session,
                title="Invalid Media",
                media_type='video',
                image_file='test.jpg'
            )
            invalid_media.full_clean()

        # Test image with video file
        with self.assertRaises(ValidationError):
            invalid_media = Media(
                session=self.session,
                title="Invalid Media",
                media_type='image',
                video_file='test.mp4'
            )
            invalid_media.full_clean()

    def test_graph_tags(self):
        """Test graph tag validation"""
        graph_media = Media.objects.create(
            session=self.session,
            title="Graph Test",
            media_type='image',
            is_graph=True,
            graph_tag='box',
            variable_tag='height'
        )
        self.assertEqual(graph_media.graph_tag, 'box')
        self.assertEqual(graph_media.variable_tag, 'height')
        self.assertTrue(graph_media.is_graph)

    def test_likes_counting(self):
        """Test likes counting methods"""
        student = Student.objects.create(
            name="Test Student",
            password="testpass",
            section=self.session,
            admin=self.admin
        )
        
        # Create interaction with likes
        interaction = StudentMediaInteraction.objects.create(
            student=student,
            media=self.media,
            liked_graph=True,
            liked_eye=True,
            liked_read=False
        )

        self.assertEqual(self.media.graph_likes_count(), 1)
        self.assertEqual(self.media.eye_likes_count(), 1)
        self.assertEqual(self.media.read_likes_count(), 0)

    def test_comment_count(self):
        """Test comment counting"""
        Comment.objects.create(
            media=self.media,
            text="Test comment",
            name="Test User"
        )
        Comment.objects.create(
            media=self.media,
            text="Another comment",
            name="Another User"
        )

        self.assertEqual(self.media.comment_count(), 2)

    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.media), "Test Media")

    def test_media_ordering(self):
        """Test default ordering"""
        media2 = Media.objects.create(
            session=self.session,
            title="Second Media",
            media_type='image'
        )
        media3 = Media.objects.create(
            session=self.session,
            title="Third Media",
            media_type='comment'
        )

        all_media = Media.objects.all()
        self.assertEqual(all_media[0], self.media)
        self.assertEqual(all_media[1], media2)
        self.assertEqual(all_media[2], media3)

