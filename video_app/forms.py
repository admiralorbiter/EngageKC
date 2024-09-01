from django import forms
from .models import Session, Media, Comment
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'border-radius: 10px; border: 1px solid #ccc; padding: 10px;',
            }),
        }

class StartSessionForm(forms.Form):
    title = forms.CharField(
        max_length=100, 
        label='Session Title',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    section = forms.IntegerField(
        label='Section Number',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    num_students = forms.IntegerField(
        label='Number of Students',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
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
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Media
        fields = ['image_file', 'graph_tag', 'variable_tag']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['graph_tag'].widget = forms.Select(choices=Media.GRAPH_TAG_CHOICES)
        self.fields['variable_tag'].widget = forms.Select(choices=Media.VARIABLE_TAG_CHOICES)
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))