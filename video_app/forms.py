from django import forms
from .models import Media, Class

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'description', 'media_type', 'video_file', 'image_file', 'class_associated']
    class_associated = forms.ModelChoiceField(queryset=Class.objects.all(), required=True)

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name']