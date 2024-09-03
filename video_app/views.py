import os
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from engagekc import settings
from .models import CustomAdmin, Media, Session, Student
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
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def post_detail(request, id):
    media = get_object_or_404(Media, id=id)
    comments = media.comments.filter(parent__isnull=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            name = request.POST.get('name')
            password = request.POST.get('password')
            device_id = request.POST.get('device_id')
            
            # Check if a student with this password exists
            try:
                student = Student.objects.get(password=password)
                new_comment = comment_form.save(commit=False)
                new_comment.media = media
                new_comment.name = student.name
                new_comment.password = password
                new_comment.device_id = device_id or student.device_id
                
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    new_comment.parent = Comment.objects.get(id=parent_id)
                
                new_comment.save()
                return redirect('post_detail', id=media.id)
            except Student.DoesNotExist:
                comment_form.add_error('password', "Invalid password.")
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

@require_POST
def like_media(request, media_id, like_type):
    media = get_object_or_404(Media, id=media_id)
    liked_media = request.session.get('liked_media', {})
    
    if str(media_id) not in liked_media:
        if like_type == 'graph':
            media.graph_likes += 1
        elif like_type == 'eye':
            media.eye_likes += 1
        elif like_type == 'read':
            media.read_likes += 1
        else:
            return JsonResponse({'error': 'Invalid like type'}, status=400)
        
        media.save()
        liked_media[str(media_id)] = like_type
        request.session['liked_media'] = liked_media
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'graph_likes': media.graph_likes,
            'eye_likes': media.eye_likes,
            'read_likes': media.read_likes
        })
    else:
        return JsonResponse({'error': 'Already liked'}, status=400)


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

            # Get the student based on the password and session
            password = form.cleaned_data['password']
            try:
                student = Student.objects.get(password=password)
                media.submitted_password = password  # Save the submitted password
            except Student.DoesNotExist:
                form.add_error('password', 'Invalid password for this session')
                return render(request, 'video_app/upload_media.html', {'form': form, 'session': session})

            # Generate the title
            graph_tag = dict(Media.GRAPH_TAG_CHOICES)[form.cleaned_data['graph_tag']]
            variable_tag = dict(Media.VARIABLE_TAG_CHOICES)[form.cleaned_data['variable_tag']]
            media.title = f"{student.name}'s {graph_tag} {variable_tag}"

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

from django.contrib.auth import get_user_model
from .models import CustomAdmin, Session

def start_session(request):
    if request.method == 'POST':
        form = StartSessionForm(request.POST)
        if form.is_valid():
            # Extract form data
            title = form.cleaned_data['title']
            section = form.cleaned_data['section']
            num_students = form.cleaned_data['num_students']
            
            # Get the CustomAdmin instance associated with the current user
            User = get_user_model()
            user = User.objects.get(username=request.user.username)
            custom_admin = CustomAdmin.objects.get(id=user.id)
            
            # Create the session object
            new_session = Session.objects.create(
                name=title,
                section=section,
                created_by=custom_admin
            )
            
            # Generate students and save them to the database
            generate_users_for_section(new_session, num_students, custom_admin)
            
            # Redirect to the admin_view page after creating the session
            return redirect('admin_view')
    else:
        form = StartSessionForm()
    
    return render(request, 'video_app/start_session.html', {'form': form})

def session_detail(request, session_pk):
    session_instance = get_object_or_404(Session, pk=session_pk)
    medias = Media.objects.filter(session=session_instance)
    
    # Get filter parameters
    graph_tag = request.GET.get('graph_tag')
    variable_tag = request.GET.get('variable_tag')

    # Apply filters
    if graph_tag:
        if graph_tag == 'true':
            medias = medias.filter(is_graph=True)
        elif graph_tag in dict(Media.GRAPH_TAG_CHOICES).keys():
            medias = medias.filter(graph_tag=graph_tag)
    if variable_tag:
        medias = medias.filter(variable_tag=variable_tag)

    # Pagination
    paginator = Paginator(medias, 12)  # Show 6 media items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    graph_choices = Media.GRAPH_TAG_CHOICES
    variable_choices = Media.VARIABLE_TAG_CHOICES

    context = {
        'session_instance': session_instance,
        'page_obj': page_obj,
        'graph_choices': graph_choices,
        'variable_choices': variable_choices,
        'selected_graph_tag': graph_tag,
        'selected_variable_tag': variable_tag,
    }
    return render(request, 'video_app/session_detail.html', context)

def join_session(request):
    sessions = Session.objects.all()
    
    if request.method == 'POST':
        session_password = request.POST.get('session_password')
        session_code = request.POST.get('session_code')
        
        if session_code:
            try:
                session_instance = Session.objects.get(session_code=session_code)
                request.session['current_session_id'] = session_instance.id
                request.session['current_session_name'] = session_instance.name
                return redirect('session_detail', session_pk=session_instance.pk)
            except Session.DoesNotExist:
                return render(request, 'video_app/join_session.html', {'error': 'Invalid session code', 'sessions': sessions})
        
        elif session_password:
            try:
                student_instance = Student.objects.get(password=session_password)
                session_instance = student_instance.section
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

from django.shortcuts import redirect
from django.urls import reverse

def filter_media(request, session_pk):
    tags = request.GET.getlist('tags')
    
    # Construct the URL with the selected tags
    url = reverse('session_detail', kwargs={'session_pk': session_pk})
    if tags:
        url += '?' + '&'.join([f'tags={tag}' for tag in tags])
    
    return redirect(url)