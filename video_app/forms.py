from django import forms
from .models import Session, Media, Comment
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'description', 'files_links', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 50}),
            'files_links': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 50}),
        }

def validate_file_size(file):
    max_size_mb = 10  # Define your size limit in MB
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Max file size is {max_size_mb}MB")

def validate_video_type(file):
    valid_mime_types = ['video/mp4', 'video/avi', 'video/mov', 'video/webm', 'video/ogg']
    if file.content_type not in valid_mime_types:
        raise ValidationError('Invalid video file type')

def validate_image_type(file):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in valid_mime_types:
        raise ValidationError('Invalid image file type')

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'description', 'media_type', 'video_file', 'image_file']

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        video_file = cleaned_data.get('video_file')
        image_file = cleaned_data.get('image_file')
        video_capture = cleaned_data.get('video_capture')
        image_capture = cleaned_data.get('image_capture')

        if media_type == 'video' and not (video_file or video_capture):
            self.add_error('video_file', 'Please upload or capture a video file.')
        elif media_type == 'video':
            file = video_file or video_capture
            validate_file_size(file)
            validate_video_type(file)

        if media_type == 'image' and not (image_file or image_capture):
            self.add_error('image_file', 'Please upload or capture an image file.')
        elif media_type == 'image':
            file = image_file or image_capture
            validate_file_size(file)
            validate_image_type(file)

        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))