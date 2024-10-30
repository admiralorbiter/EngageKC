from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from video_app.models import Session, Media, Student, StudentMediaInteraction, Comment
from datetime import timedelta
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Generates test data for the application'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.CustomAdmin = get_user_model()
        
        # Constants for data generation
        self.SCHOOLS = [
            ('Lincoln High School', 'Lincoln District'),
            ('Washington High School', 'Washington District'),
            ('Roosevelt Middle School', 'Roosevelt District'),
            ('Jefferson Academy', 'Jefferson District'),
        ]
        
        self.IMAGE_FILES = ['test1.PNG', 'test2.png', 'test3.png', 'test4.png']
        self.GRAPH_TAGS = ['box', 'histogram', 'comparison']
        self.VARIABLE_TAGS = [
            'gender', 'languages', 'handedness', 'eye_color', 'hair_color',
            'height', 'arm_span', 'travel_method', 'bed_time', 'wake_time',
            'sport_activity', 'screen_time', 'pineapple_pizza', 'ice_cream',
            'cats_or_dogs', 'happiness', 'climate_change', 'reaction_time'
        ]
        
        self.COMMENT_TEMPLATES = [
            "I notice that...",
            "This reminds me of...",
            "I wonder why...",
            "The pattern shows...",
            "Interesting how...",
            "This data suggests...",
            "Could this mean that...",
            "The trend indicates...",
        ]

    def create_admins(self, num_admins=8):
        admins = []
        for i in range(num_admins):
            school, district = random.choice(self.SCHOOLS)
            admin = self.CustomAdmin.objects.create_user(
                username=f'teacher{i+1}',
                email=f'teacher{i+1}@example.com',
                password='password123',
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                school=school,
                district=district,
                is_staff=True
            )
            admins.append(admin)
            self.stdout.write(f'Created admin: {admin.username} at {school}')
        return admins

    def create_sessions(self, admins):
        sessions = []
        # Each admin gets 1-8 sections
        for i, admin in enumerate(admins):
            num_sections = random.randint(1, 8)
            self.stdout.write(f'Creating {num_sections} sections for {admin.username}')
            
            for section_num in range(num_sections):
                session = Session.objects.create(
                    name=f"Period {section_num + 1}",
                    section=section_num + 1,
                    created_by=admin,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                    is_paused=random.choice([True, False]),
                    character_set=random.choice(['marvel', 'dc', 'starwars'])
                )
                sessions.append(session)
        return sessions

    def create_students(self, sessions, num_students=1000):
        students = []
        for session in sessions:
            # Random number of students (15-30) per session
            num_session_students = random.randint(15, 30)
            for _ in range(num_session_students):
                student = Student.objects.create(
                    name=self.fake.name(),
                    password=f"pass{random.randint(1000, 9999)}",
                    section=session,
                    admin=session.created_by,
                    character_description=self.fake.text(max_nb_chars=100),
                    avatar_image_path=f"avatars/avatar{random.randint(1, 10)}.png"
                )
                students.append(student)
        return students

    def create_media(self, sessions):
        media_items = []
        base_date = timezone.now() - timedelta(days=30)
        
        self.stdout.write('Creating media items...')
        
        # First ensure each session has 100 posts
        for i, session in enumerate(sessions):
            self.stdout.write(f'Creating media for session {i+1}/{len(sessions)}')
            
            for j in range(100):  # 100 posts per session
                is_graph = random.choice([True, False])
                image_name = random.choice(self.IMAGE_FILES)
                media = Media(
                    session=session,
                    title=f"Media {session.section}-{j+1}",
                    description=f"This is media upload {j+1} for section {session.section}.",
                    media_type='image',
                    image_file=f"static/video_app/images/{image_name}",  # Updated path
                    uploaded_at=base_date + timedelta(minutes=j),
                    graph_tag=random.choice(self.GRAPH_TAGS) if is_graph else None,
                    is_graph=is_graph,
                    variable_tag=random.choice(self.VARIABLE_TAGS) if is_graph else None
                )
                media_items.append(media)
                
                if len(media_items) >= 1000:
                    Media.objects.bulk_create(media_items)
                    media_items = []
        
        if media_items:
            Media.objects.bulk_create(media_items)
            
        return list(Media.objects.all())

    def create_interactions(self, students, media_items):
        batch_size = 1000
        interactions = []
        
        self.stdout.write('Preparing interactions...')
        total_students = len(students)
        
        for i, student in enumerate(students):
            if i % 10 == 0:  # More frequent progress updates
                self.stdout.write(f'Processing student {i}/{total_students}...')
            
            # Get media items from student's session
            session_media = [m for m in media_items if m.session_id == student.section_id]
            
            # Interact with 20-40% of session's media
            num_interactions = random.randint(
                len(session_media) // 5,  # 20%
                len(session_media) * 2 // 5  # 40%
            )
            
            for media in random.sample(session_media, num_interactions):
                interactions.append(StudentMediaInteraction(
                    student=student,
                    media=media,
                    liked_graph=random.choice([True, False]),
                    liked_eye=random.choice([True, False]),
                    liked_read=random.choice([True, False]),
                    comment_count=random.randint(0, 5)
                ))
                
                if len(interactions) >= batch_size:
                    StudentMediaInteraction.objects.bulk_create(interactions)
                    interactions = []
        
        if interactions:
            StudentMediaInteraction.objects.bulk_create(interactions)

    def create_comments(self, students, media_items, num_comments_per_media=5):
        batch_size = 1000
        comments = []
        
        self.stdout.write('Preparing comments...')
        total_media = len(media_items)
        
        for i, media in enumerate(media_items):
            if i % 100 == 0:  # Progress update every 100 media items
                self.stdout.write(f'Processing media {i}/{total_media}...')
            
            # Get students from the same session
            session_students = [s for s in students if s.section_id == media.session_id]
            
            if session_students:  # Make sure there are students in the session
                # Create 3-7 comments per media
                num_comments = random.randint(3, 7)
                commenting_students = random.sample(
                    session_students,
                    min(num_comments, len(session_students))
                )
                
                for student in commenting_students:
                    comments.append(Comment(
                        media=media,
                        text=random.choice(self.COMMENT_TEMPLATES) + " " + self.fake.sentence(),
                        name=student.name,
                        student=student,
                        is_admin=False,
                        created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                    ))
                    
                    if len(comments) >= batch_size:
                        Comment.objects.bulk_create(comments)
                        comments = []
        
        if comments:
            Comment.objects.bulk_create(comments)

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        self.CustomAdmin.objects.all().delete()
        Session.objects.all().delete()
        Media.objects.all().delete()
        Student.objects.all().delete()
        Comment.objects.all().delete()
        StudentMediaInteraction.objects.all().delete()

        # Create new data
        self.stdout.write('Creating admins...')
        admins = self.create_admins()
        
        self.stdout.write('Creating sessions...')
        sessions = self.create_sessions(admins)
        
        self.stdout.write('Creating students...')
        students = self.create_students(sessions)
        
        self.stdout.write('Creating media...')
        media_items = self.create_media(sessions)
        
        self.stdout.write('Creating interactions...')
        self.create_interactions(students, media_items)
        
        self.stdout.write('Creating comments...')
        self.create_comments(students, media_items)

        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))