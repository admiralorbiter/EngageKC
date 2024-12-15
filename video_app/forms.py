from django import forms
from .models import Session, Media, Comment
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .utils import get_available_character_sets

class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = Comment
        fields = ['text']

class StartSessionForm(forms.ModelForm):
    num_students = forms.IntegerField(min_value=1, max_value=100)
    district = forms.CharField(max_length=100)
    school = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    module = forms.ChoiceField(choices=Session.MODULE_CHOICES)

    class Meta:
        model = Session
        fields = ['section', 'num_students']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section'].widget.attrs.update({'class': 'form-control'})
        self.fields['num_students'].widget.attrs.update({'class': 'form-control'})
        self.fields['district'].widget.attrs.update({'class': 'form-control'})
        self.fields['school'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

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
        fields = ['image_file', 'graph_tag', 'variable_tag']
        widgets = {
            'image_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'graph_tag': forms.Select(attrs={
                'class': 'form-select'
            }),
            'variable_tag': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_file'].label = 'Image File'
        self.fields['graph_tag'].label = 'Graph Type'
        self.fields['variable_tag'].label = 'Variable Tag'

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
