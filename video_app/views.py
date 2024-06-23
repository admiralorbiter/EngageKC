from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
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

@login_required
def delete_media(request, pk):
    media = get_object_or_404(Media, pk=pk)
    if request.method == 'POST':
        media.delete()
        return redirect('media_list')
    return render(request, 'video_app/delete_media.html', {'media': media})