from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Media, Session
from .forms import MediaForm, SessionForm
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

def upload_media(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.session_associated = session
            media.save()
            return redirect('session_detail', pk=session.id)
    else:
        form = MediaForm()
    return render(request, 'video_app/upload_media.html', {'form': form, 'session': session})

@login_required
def delete_media(request, pk):
    media = get_object_or_404(Media, pk=pk)
    if request.method == 'POST':
        media.delete()
        return redirect('media_list')
    return render(request, 'video_app/delete_media.html', {'media': media})

def start_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            new_session = form.save()
            return redirect('session_detail', pk=new_session.pk)
    else:
        form = SessionForm()
    return render(request, 'video_app/start_session.html', {'form': form})

def session_detail(request, pk):
    session_instance = get_object_or_404(Session, pk=pk)
    medias = session_instance.media.all()
    return render(request, 'video_app/session_detail.html', {'session_instance': session_instance, 'medias': medias})

def join_session(request):
    sessions = Session.objects.all()
    if request.method == 'POST':
        session_code = request.POST.get('session_code')
        try:
            session_instance = Session.objects.get(session_code=session_code)
            return redirect('session_detail', pk=session_instance.pk)
        except Session.DoesNotExist:
            return render(request, 'video_app/join_session.html', {'error': 'Invalid session code', 'sessions': sessions})
    return render(request, 'video_app/join_session.html', {'sessions': sessions})