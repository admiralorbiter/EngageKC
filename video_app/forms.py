from django import forms
from .models import Session, Media

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'description', 'files_links', 'notes']

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'description', 'media_type', 'video_file', 'image_file']