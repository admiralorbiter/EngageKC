from django.core.management.base import BaseCommand
from video_app.models import Session, Media, CustomAdmin
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates a TESTING session with sample media items'

    def handle(self, *args, **options):
        # Create or get the CustomAdmin
        admin, created = CustomAdmin.objects.get_or_create(
            username="testadmin",
            defaults={
                "school": "Test School",
                "district": "Test District",
                "first_name": "Test",
                "last_name": "Admin"
            }
        )
        if created:
            admin.set_password("testpassword")
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created test admin user'))

        # Create the TESTING session
        session, created = Session.objects.get_or_create(
            name="TESTING",
            defaults={
                "section": 1,
                "created_by": admin,
                "created_at": timezone.now()
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created TESTING session'))
        else:
            self.stdout.write(self.style.SUCCESS('TESTING session already exists'))

        # Create sample media items
        for i in range(1, 60):
            media_data = {
                "title": f"Test Media {i}",
                "session": session,
                "description": f"This is test media upload {i}.",
                "media_type": "image",
                "image_file": "images/test2.png",
                "uploaded_at": timezone.now(),
            }
            
            # Every 5th item is a graph
            if i % 5 == 0:
                media_data.update({
                    "is_graph": True,
                    "graph_tag": "bar",  # or randomly choose from GRAPH_TAG_CHOICES
                    "variable_tags": ["gender", "height"],  # You can add multiple tags
                })
            
            media, created = Media.objects.get_or_create(
                title=media_data["title"],
                defaults=media_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created media item: {media.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Media item already exists: {media.title}'))

        self.stdout.write(self.style.SUCCESS('Test session setup complete'))
