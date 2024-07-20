from django import forms
from .models import Session, Media
from django.contrib.auth.forms import AuthenticationForm

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'description', 'files_links', 'notes']

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'description', 'media_type', 'video_file', 'image_file']

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        video_file = cleaned_data.get('video_file')
        image_file = cleaned_data.get('image_file')

        if media_type == 'video' and not video_file:
            raise forms.ValidationError('A video file is required for the selected media type.')
        if media_type == 'image' and not image_file:
            raise forms.ValidationError('An image file is required for the selected media type.')

        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))