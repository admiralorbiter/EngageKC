from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Media, Session
from .forms import MediaForm, SessionForm, LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth import views
from django.contrib.auth.decorators import user_passes_test

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
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.session = session
            media.save()
            return redirect('session_detail', session_pk=session.pk)
        else:
            print(form.errors)
    else:
        form = MediaForm()

    return render(request, 'video_app/upload_media.html', {'form': form, 'session': session})
   

@user_passes_test(lambda u: u.is_superuser)
def delete_media(request, pk):
    media = get_object_or_404(Media, pk=pk)
    if request.method == 'POST':
        session_pk = media.session.pk  # Save the session primary key before deleting the media
        media.delete()
        return redirect('session_detail', pk=session_pk)
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
    medias = session_instance.media.all()  # Use the related_name 'media'
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