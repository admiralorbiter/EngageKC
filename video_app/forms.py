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

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))