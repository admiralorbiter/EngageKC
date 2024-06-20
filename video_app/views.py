from django.shortcuts import render, redirect
from .models import Video
from .forms import VideoForm

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_app/video_list.html', {'videos': videos})

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('video_list')
    else:
        form = VideoForm()
    return render(request, 'video_app/upload_video.html', {'form': form})
