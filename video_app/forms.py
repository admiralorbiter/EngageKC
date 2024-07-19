from django import forms
from .models import Media, Session

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'description', 'media_type', 'video_file', 'image_file', 'session_associated']
    session_associated = forms.ModelChoiceField(queryset=Session.objects.all(), required=True)

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'description', 'files_links', 'notes']
