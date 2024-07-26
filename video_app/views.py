from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Media, Session
from .forms import MediaForm, SessionForm, LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth import views
from django.contrib.auth.decorators import user_passes_test
import base64
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Media, Comment
from .forms import CommentForm

def post_detail(request, id):
    media = get_object_or_404(Media, id=id)
    comments = media.comments.filter(parent__isnull=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.media = media
            new_comment.device_id = request.POST.get('device_id')  # Save the device ID with the comment
            print(new_comment.device_id)
            if request.POST.get('parent_id'):
                parent_id = int(request.POST.get('parent_id'))
                new_comment.parent = Comment.objects.get(id=parent_id)
            new_comment.save()
            return redirect('post_detail', id=media.id)
    else:
        comment_form = CommentForm()

    return render(request, 'video_app/post_detail.html', {
        'media': media,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form
    })

def pause_session(request, session_pk):
    session = get_object_or_404(Session, id=session_pk)
    session.is_paused = not(session.is_paused)
    session.save()
    return redirect('join_session')

@user_passes_test(lambda u: u.is_superuser)
def delete_session(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk)
    session.delete()
    return redirect('join_session')

def like_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    liked_media = request.session.get('liked_media', [])
    
    if media_id not in liked_media:
        media.likes += 1
        media.save()
        liked_media.append(media_id)
        request.session['liked_media'] = liked_media
        messages.success(request, 'You liked this media.')
    else:
        messages.info(request, 'You have already liked this media.')
    
    return redirect('session_detail', session_pk=media.session.pk)


class AdminLoginView(views.LoginView):
    template_name = 'video_app/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

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
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(f"Username: {username}, Password: {password}")  # Debugging output
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                print("Test 2")
                return render(request, 'video_app/login.html', {'form': form, 'error': 'Invalid username or password'})
        else:
            return render(request, 'video_app/login.html', {'form': form, 'error': 'Invalid form submission'})
    else:
        form = LoginForm()
    return render(request, 'video_app/login.html', {'form': form})

def index(request):
    return render(request, 'video_app/index.html')

def upload_media(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk)

    if request.method == 'POST':
        captured_image_data = request.POST.get('captured_image_data')
        captured_video_data = request.POST.get('captured_video_data')

        # Check if there's any captured image or video data
        if captured_image_data:
            format, imgstr = captured_image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'captured_image.{ext}')
            request.FILES['image_file'] = data

        if captured_video_data:
            format, vidstr = captured_video_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(vidstr), name=f'captured_video.{ext}')
            content_type = 'video/webm'  # Adjust this according to the actual video format you are using
            video_file = SimpleUploadedFile(f'captured_video.{ext}', base64.b64decode(vidstr), content_type=content_type)
            request.FILES['video_file'] = video_file

        form = MediaForm(request.POST, request.FILES)
        
        if form.is_valid():
            media = form.save(commit=False)
            media.session = session
            media.save()
            return redirect('session_detail', session_pk=session.pk)
        else:
            print("Form errors:", form.errors)
    else:
        form = MediaForm()

    return render(request, 'video_app/upload_media.html', {'form': form, 'session': session})
   

@user_passes_test(lambda u: u.is_superuser)
def delete_media(request, session_pk):
    media = get_object_or_404(Media, pk=session_pk)
    if request.method == 'POST':
        session_pk = media.session.pk  # Save the session primary key before deleting the media
        media.delete()
        return redirect('session_detail', session_pk=session_pk)
    return render(request, 'video_app/delete_media.html', {'media': media})

def start_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            new_session = form.save(commit=False)  # Use commit=False to get the object but not save it to the database yet
            new_session.created_by = str(request.user)
            new_session.save()  # Now save the session with the updated created_by field
            return redirect('session_detail', session_pk=new_session.pk)
    else:
        form = SessionForm()
    return render(request, 'video_app/start_session.html', {'form': form})


def session_detail(request, session_pk):
    session_instance = get_object_or_404(Session, pk=session_pk)
    medias = session_instance.media.all()
    return render(request, 'video_app/session_detail.html', {
        'session_instance': session_instance,
        'medias': medias,
    })

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