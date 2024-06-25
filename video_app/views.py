from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Media, Class
from .forms import MediaForm, ClassForm
from django.contrib.auth.forms import UserCreationForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    return render(request, 'video_app/login.html')

def index(request):
    return render(request, 'video_app/index.html')

def media_list(request):
    medias = Media.objects.all()
    if not request.user.is_authenticated:
        return render(request, 'video_app/media_list_loggedout.html', {'medias': medias})
    return render(request, 'video_app/media_list.html', {'medias': medias})

def upload_media(request):
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media=form.save()
            return redirect('class_detail', pk=media.class_associated.pk)

    else:
        form = MediaForm()
    return render(request, 'video_app/upload_media.html', {'form': form})

@login_required
def delete_media(request, pk):
    media = get_object_or_404(Media, pk=pk)
    if request.method == 'POST':
        media.delete()
        return redirect('media_list')
    return render(request, 'video_app/delete_media.html', {'media': media})

def start_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            new_class = form.save()
            return redirect('class_detail', pk=new_class.pk)
    else:
        form = ClassForm()
    return render(request, 'video_app/start_class.html', {'form': form})

def class_detail(request, pk):
    class_instance = get_object_or_404(Class, pk=pk)
    medias = class_instance.media.all()
    return render(request, 'video_app/class_detail.html', {'class_instance': class_instance, 'medias': medias})

def join_class(request):
    classes = Class.objects.all()
    if request.method == 'POST':
        class_code = request.POST.get('class_code')
        try:
            class_instance = Class.objects.get(class_code=class_code)
            return redirect('class_detail', pk=class_instance.pk)
        except Class.DoesNotExist:
            return render(request, 'video_app/join_class.html', {'error': 'Invalid class code', 'classes': classes})
    return render(request, 'video_app/join_class.html', {'classes': classes})