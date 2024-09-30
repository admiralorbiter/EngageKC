from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from video_app.models import CustomAdmin

class Command(BaseCommand):
    help = 'Creates 5 custom admin accounts for teachers'

    def handle(self, *args, **options):
        CustomAdmin = get_user_model()
        
        teachers = [
            {
                'username': 'teacher1',
                'email': 'teacher1@example.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'school': 'High School 1',
                'district': 'District A'
            },
            {
                'username': 'teacher2',
                'email': 'teacher2@example.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'school': 'Middle School 2',
                'district': 'District B'
            },
            # Add 3 more teacher dictionaries here
        ]

        for teacher in teachers:
            try:
                user = CustomAdmin.objects.create_user(
                    username=teacher['username'],
                    email=teacher['email'],
                    password=teacher['password'],
                    first_name=teacher['first_name'],
                    last_name=teacher['last_name'],
                    school=teacher['school'],
                    district=teacher['district']
                )
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created admin account for {teacher["username"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create admin account for {teacher["username"]}: {str(e)}'))

