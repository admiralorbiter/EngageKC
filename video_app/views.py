from django.shortcuts import render, redirect
from .models import Media
from .forms import MediaForm

def media_list(request):
    medias = Media.objects.all()
    return render(request, 'video_app/media_list.html', {'medias': medias})

def upload_media(request):
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('media_list')
    else:
        form = MediaForm()
    return render(request, 'video_app/upload_media.html', {'form': form})
