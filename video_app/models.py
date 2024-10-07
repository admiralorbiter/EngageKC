from django.db import models
import uuid
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

from engagekc import settings

class Session(models.Model):
    name = models.CharField(max_length=100)
    session_code = models.CharField(max_length=8, unique=True, editable=False)
    section = models.IntegerField()

    def clean(self):
        if self.section < 0:
            raise ValidationError("Section number cannot be negative.")

    def save(self, *args, **kwargs):
        if not self.session_code:
            self.session_code = uuid.uuid4().hex[:8].upper()
        self.full_clean()
        super().save(*args, **kwargs)

    created_at = models.DateTimeField(auto_now_add=True)
    is_paused = models.BooleanField(default=False)
    created_by = models.ForeignKey('CustomAdmin', on_delete=models.SET_NULL, blank=True, null=True)

    def is_expired(self):
        return not self.is_paused and (timezone.now() > self.created_at + timedelta(days=7))
    
    def days_until_deletion(self):
        if self.is_paused:
            return 'Paused'
        days_left = 360 - (timezone.now() - self.created_at).days
        return max(0, days_left)

    def __str__(self):
        return self.name

class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('comment', 'Comment'),
    )
    TAG_CHOICES = [
        ('education', 'Education'),
        ('announcement', 'Announcement'),
        ('discussion', 'Discussion'),
        ('other', 'Other'),
    ]
    session = models.ForeignKey(Session, related_name='media', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    image_file = models.ImageField(upload_to='images', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=50, choices=TAG_CHOICES, default='education')
    
    # New fields for likes
    graph_likes = models.PositiveIntegerField(default=0)
    eye_likes = models.PositiveIntegerField(default=0)
    read_likes = models.PositiveIntegerField(default=0)

    GRAPH_TAG_CHOICES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Graph'),
        ('pie', 'Pie Chart'),
        ('box', 'Box Plot'),
        ('histogram', 'Histogram'),
        ('comparison', 'Comparison'),
    ]
    VARIABLE_TAG_CHOICES = [
        ('gender', 'Gender'),
        ('languages', 'Languages'),
        ('handedness', 'Handedness'),
        ('eye_color', 'Eye Color'),
        ('hair_color', 'Hair Color'),
        ('hair_type', 'Hair Type'),
        ('height', 'Height'),
        ('left_foot_length', 'Left Foot Length'),
        ('right_foot_length', 'Right Foot Length'),
        ('longer_foot', 'Longer Foot'),
        ('index_finger', 'Index Finger'),
        ('ring_finger', 'Ring Finger'),
        ('longer_finger', 'Longer Finger'),
        ('arm_span', 'Arm Span'),
        ('travel_method', 'Travel Method to School'),
        ('bed_time', 'Bed Time'),
        ('wake_time', 'Wake Time'),
        ('sport_activity', 'Sport or Activity'),
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('snapchat', 'Snapchat'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('tiktok', 'TikTok'),
        ('twitch', 'Twitch'),
        ('pinterest', 'Pinterest'),
        ('bereal', 'BeReal'),
        ('whatsapp', 'WhatsApp'),
        ('discord', 'Discord'),
        ('screen_time', 'Screen Time After School'),
        ('pineapple_pizza', 'Pineapple on Pizza'),
        ('ice_cream', 'Ice Cream'),
        ('cats_or_dogs', 'Cats or Dogs'),
        ('happiness', 'Happiness'),
        ('climate_change', 'Climate Change'),
        ('reaction_time', 'Reaction Time'),
        ('memory_test', 'Memory Test'),
    ]

    # Use CharField for specific graph types
    graph_tag = models.CharField(max_length=50, choices=GRAPH_TAG_CHOICES, blank=True, null=True)
    # Use BooleanField for general graph indicator
    is_graph = models.BooleanField(default=False)
    variable_tag = models.CharField(max_length=50, choices=VARIABLE_TAG_CHOICES, blank=True, null=True)

    submitted_password = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        if self.media_type == 'video' and self.image_file:
            raise ValidationError('Cannot upload an image file for a video media type')
        if self.media_type == 'image' and self.video_file:
            raise ValidationError('Cannot upload a video file for an image media type')

    def __str__(self):
        return self.title

    def comment_count(self):
        return self.comments.count()

    class Meta:
        ordering = ['id']  # Default ordering, will be overridden in the view

    def graph_likes_count(self):
        return self.student_interactions.filter(liked_graph=True).count()

    def eye_likes_count(self):
        return self.student_interactions.filter(liked_eye=True).count()

    def read_likes_count(self):
        return self.student_interactions.filter(liked_read=True).count()

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

class CustomAdmin(AbstractUser):
    school = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    media_password = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_admin_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_admin_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return f"{self.username} - {self.school} ({self.district})"

class Student(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    section = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='students')
    admin = models.ForeignKey(CustomAdmin, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    character_description = models.TextField(blank=True, null=True)
    avatar_image_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.section})"

    def get_media_interaction(self, media):
        return self.media_interactions.filter(media=media).first()

class StudentMediaInteraction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='media_interactions')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='student_interactions')
    liked_graph = models.BooleanField(default=False)
    liked_eye = models.BooleanField(default=False)
    liked_read = models.BooleanField(default=False)
    comment_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'media')

    def __str__(self):
        return f"{self.student.name} - {self.media.title} Interaction"

class Comment(models.Model):
    media = models.ForeignKey(Media, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    
    def __str__(self):
        return f'Comment by {self.name} on {self.media.title}'