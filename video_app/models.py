from django.db import models
import uuid

class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('video', 'Video'),
        ('image', 'Image'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Class(models.Model):
    name = models.CharField(max_length=100)
    class_code = models.CharField(max_length=8, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.class_code:
            self.class_code = str(uuid.uuid4())[:8]  # Generate an 8-character unique code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name