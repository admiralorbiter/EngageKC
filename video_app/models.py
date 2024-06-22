from django.db import models

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
