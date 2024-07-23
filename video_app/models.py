from django.db import models
import uuid
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
from django.utils import timezone
from datetime import timedelta

from jsonschema import ValidationError

class Session(models.Model):
    name = models.CharField(max_length=100)
    session_code = models.CharField(max_length=8, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    files_links = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paused = models.BooleanField(default=False)

    def is_expired(self):
        return not self.is_paused and (timezone.now() > self.created_at + timedelta(days=7))
    
    def save(self, *args, **kwargs):
        if not self.session_code:
            self.session_code = str(uuid.uuid4())[:8]  # Generate an 8-character unique code
        super().save(*args, **kwargs)

    def days_until_deletion(self):
        if self.is_paused:
            return 'Paused'
        days_left = 7 - (timezone.now() - self.created_at).days
        return max(0, days_left)

    def __str__(self):
        return self.name

class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('comment', 'Comment'),
    )
    session = models.ForeignKey(Session, related_name='media', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    image_file = models.ImageField(upload_to='images', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)  # New field to track likes


    def clean(self):
        if self.media_type == 'video' and self.image_file:
            raise ValidationError('Cannot upload an image file for a video media type')
        if self.media_type == 'image' and self.video_file:
            raise ValidationError('Cannot upload a video file for an image media type')

    def __str__(self):
        return self.title

@receiver(pre_delete, sender=Session)
def delete_associated_media(sender, instance, **kwargs):
    media_files = instance.media.all()
    print(f"Found {media_files.count()} media files associated with the session")
    for media in media_files:
        if media.media_type == 'video' and media.video_file:
            print(f"Deleting video file: {media.video_file.path}")
            if os.path.isfile(media.video_file.path):
                try:
                    os.remove(media.video_file.path)
                    print(f"Successfully deleted video file: {media.video_file.path}")
                except Exception as e:
                    print(f"Error deleting video file {media.video_file.path}: {e}")
            else:
                print(f"Video file does not exist: {media.video_file.path}")
        elif media.media_type == 'image' and media.image_file:
            print(f"Deleting image file: {media.image_file.path}")
            if os.path.isfile(media.image_file.path):
                try:
                    os.remove(media.image_file.path)
                    print(f"Successfully deleted image file: {media.image_file.path}")
                except Exception as e:
                    print(f"Error deleting image file {media.image_file.path}: {e}")
            else:
                print(f"Image file does not exist: {media.image_file.path}")
        media.delete()

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
