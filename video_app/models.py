from django.db import models
import uuid

from jsonschema import ValidationError

class Session(models.Model):
    name = models.CharField(max_length=100)
    session_code = models.CharField(max_length=8, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    files_links = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.session_code:
            self.session_code = str(uuid.uuid4())[:8]  # Generate an 8-character unique code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('comment', 'Comment'),
    )
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='media')
    title = models.CharField(max_length=100)
    description = models.TextField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.media_type == 'video' and self.image_file:
            raise ValidationError('Cannot upload an image file for a video media type')
        if self.media_type == 'image' and self.video_file:
            raise ValidationError('Cannot upload a video file for an image media type')

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.PositiveIntegerField(default=0)
    links = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.id} on {self.post.title}'
