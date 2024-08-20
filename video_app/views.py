import os
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from engagekc import settings
from .models import Media, Session, Student
from .forms import MediaForm, LoginForm, StartSessionForm
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
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import openpyxl


def post_detail(request, id):
    media = get_object_or_404(Media, id=id)
    comments = media.comments.filter(parent__isnull=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.media = media
            new_comment.device_id = request.POST.get('device_id')
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

# Paths to your files
NAMES_FILE_PATH = os.path.join(settings.BASE_DIR, 'video_app', 'static', 'video_app', 'names.txt')
WORDS_FILE_PATH = os.path.join(settings.BASE_DIR, 'video_app', 'static', 'video_app', 'words.txt')

def load_names():
    """Load names from the names.txt file."""
    with open(NAMES_FILE_PATH, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def load_words():
    """Load words from the words.txt file."""
    with open(WORDS_FILE_PATH, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def generate_passcode(words):
    """Generates a 4-word passcode from the loaded word list."""
    return '.'.join(random.sample(words, 2))

def generate_users_for_section(section, num_students, admin):
    """Generates students with random names and passcodes for a given section, saving them to the database."""
    names_list = load_names()
    words_list = load_words()
    
    generated_students = []
    
    for _ in range(num_students):
        # Pick a unique name that is not already used in the database
        while True:
            name = random.choice(names_list)
            if not Student.objects.filter(name=name).exists():  # Check if name is already used in the database
                break
        
        # Generate the 4-word passcode
        passcode = generate_passcode(words_list)
        
        # Save the student to the database
        student = Student.objects.create(
            name=name,
            password=passcode,
            section=section,
            admin=admin 
        )
        
        generated_students.append(student)
    
    return generated_students


def start_session(request):
    if request.method == 'POST':
        form = StartSessionForm(request.POST)
        if form.is_valid():
            # Extract form data
            title = form.cleaned_data['title']
            section = form.cleaned_data['section']
            num_students = form.cleaned_data['num_students']
            
            # Create the session object
            new_session = Session.objects.create(
                name=title,
                section=section,
                created_by=str(request.user)
            )
            
            # Generate students and save them to the database
            generate_users_for_section(new_session, num_students, request.user)
            
            # Redirect to the session detail page or any other page
            return redirect('session_detail', session_pk=new_session.pk)
    else:
        form = StartSessionForm()
    
    return render(request, 'video_app/start_session.html', {'form': form})

def session_detail(request, session_pk):
    session_instance = get_object_or_404(Session, pk=session_pk)
    tags = Media.TAG_CHOICES
    selected_tags = request.GET.getlist('tags')
    if selected_tags:
        medias = Media.objects.filter(session=session_instance, tag__in=selected_tags).distinct()
    else:
        medias = Media.objects.filter(session=session_instance)

    context = {
        'session_instance': session_instance,
        'medias': medias,
        'tags': tags,
        'selected_tags': selected_tags,
    }
    return render(request, 'video_app/session_detail.html', context)

def join_session(request):
    sessions = Session.objects.all()
    
    if request.method == 'POST':
        session_password = request.POST.get('session_password')
        try:
            # Attempt to find a student with the given password
            student_instance = Student.objects.get(password=session_password)
            
            # Retrieve the associated session via the section ForeignKey
            session_instance = student_instance.section
            
            # Store session information in user's session
            request.session['current_session_id'] = session_instance.id
            request.session['current_session_name'] = session_instance.name
            
            return redirect('session_detail', session_pk=session_instance.pk)
        except Student.DoesNotExist:
            return render(request, 'video_app/join_session.html', {'error': 'Invalid session password', 'sessions': sessions})
    
    return render(request, 'video_app/join_session.html', {'sessions': sessions})

@user_passes_test(lambda u: u.is_superuser)
def admin_view(request):
    # Get all sessions and students related to the logged-in admin
    sessions = Session.objects.filter(created_by=request.user)
    students = Student.objects.filter(admin=request.user)

    return render(request, 'video_app/admin_view.html', {
        'sessions': sessions,
        'students': students,
    })

def delete_student(request, student_id):
    # Get the student object or return a 404 if not found
    student = get_object_or_404(Student, id=student_id)

    # Ensure the logged-in user is the admin of the student
    if student.admin == request.user:
        student.delete()

    # Redirect back to the admin view after deletion
    return redirect('admin_view')

@user_passes_test(lambda u: u.is_superuser)
def download_students(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Students'

    # Write the header
    headers = ['Name', 'Passcode', 'Section']
    for col_num, header in enumerate(headers, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = header

    # Write the data
    students = Student.objects.all()
    for row_num, student in enumerate(students, 2):
        row = [
            student.name,
            student.password,
            student.section.name if student.section else 'N/A'  # Use the session name instead of the entire object
        ]
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    workbook.save(response)
    return response

@user_passes_test(lambda u: u.is_superuser)
def generate_students(request):
    if request.method == 'POST':
        num_students = int(request.POST.get('num_students', 0))
        section_id = request.POST.get('section')
        
        if num_students > 0 and section_id:
            try:
                session = Session.objects.get(id=section_id)
                generated_students = generate_users_for_section(session, num_students, request.user)
                
                messages.success(request, f"{len(generated_students)} new students generated for {session.name}")
            except Session.DoesNotExist:
                messages.error(request, "Invalid session selected. Please try again.")
        else:
            messages.error(request, "Invalid input. Please try again.")
    
    return redirect('admin_view')