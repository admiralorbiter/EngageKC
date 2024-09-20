import os
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

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
from django.db.models import Sum, Count, F, Q, Case, When, IntegerField
from django.db.models.functions import Coalesce

from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def post_detail(request, id):
    media = get_object_or_404(Media, id=id)
    comments = media.comments.filter(parent__isnull=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.media = media

            student = None
            if 'student_id' in request.session:
                student = Student.objects.filter(id=request.session['student_id']).first()

            if student:
                new_comment.name = student.name
                new_comment.is_admin = False
                new_comment.student = student  # Set the student field
            elif request.user.is_staff or request.user.is_superuser:
                new_comment.name = f"Admin: {request.user.username}"
                new_comment.is_admin = True
            else:
                messages.error(request, 'You do not have permission to comment on this media.')
                return redirect('post_detail', id=media.id)

            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)
            
            new_comment.save()
            
            # Update the comment count for the student's media interaction
            if student:
                interaction, _ = StudentMediaInteraction.objects.get_or_create(student=student, media=media)
                interaction.comment_count += 1
                interaction.save()

            messages.success(request, 'Your comment has been added successfully.')
            return redirect('post_detail', id=media.id)
        else:
            messages.error(request, 'There was an error with your comment. Please try again.')
    else:
        comment_form = CommentForm()

    context = {
        'media': media,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form
    }

    return render(request, 'video_app/post_detail.html', context)

def pause_session(request, session_pk):
    session = get_object_or_404(Session, id=session_pk)
    session.is_paused = not(session.is_paused)
    session.save()
    return redirect('join_session')

@login_required
def delete_session(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk)
    session.delete()
    return redirect('join_session')

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Media, Student, StudentMediaInteraction
from django.db.models import F
from django.db import transaction

@require_POST
def like_media(request, media_id, like_type):
    # Check if a student is logged in
    student = None
    if 'student_id' in request.session:
        student = Student.objects.filter(id=request.session['student_id']).first()
    
    # If no student is logged in or the user is an admin, return an error
    if not student or request.user.is_staff:
        return JsonResponse({'error': 'Only logged-in students can vote'}, status=403)

    media = get_object_or_404(Media, id=media_id)
    
    with transaction.atomic():
        interaction, created = StudentMediaInteraction.objects.get_or_create(
            student=student,
            media=media
        )
        
        # Reset all likes for this interaction
        interaction.liked_graph = False
        interaction.liked_eye = False
        interaction.liked_read = False
        
        # Set the new like
        if like_type == 'graph':
            interaction.liked_graph = True
        elif like_type == 'eye':
            interaction.liked_eye = True
        elif like_type == 'read':
            interaction.liked_read = True
        else:
            return JsonResponse({'error': 'Invalid like type'}, status=400)
        
        interaction.save()
    
    # Recalculate likes
    graph_likes = StudentMediaInteraction.objects.filter(media=media, liked_graph=True).count()
    eye_likes = StudentMediaInteraction.objects.filter(media=media, liked_eye=True).count()
    read_likes = StudentMediaInteraction.objects.filter(media=media, liked_read=True).count()
    
    # Update Media object
    media.graph_likes = graph_likes
    media.eye_likes = eye_likes
    media.read_likes = read_likes
    media.save()
    
    return JsonResponse({
        'success': True,
        'graph_likes': graph_likes,
        'eye_likes': eye_likes,
        'read_likes': read_likes,
        'user_like': like_type
    })

# Add this function to update comment count
def update_comment_count(student, media):
    interaction, created = StudentMediaInteraction.objects.get_or_create(
        student=student,
        media=media
    )
    interaction.comment_count += 1
    interaction.save()

# In your post_detail view or wherever comments are added, call this function:
# update_comment_count(student, media)


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
    print("Login view called")
    print(request.user.is_staff)
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

from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

@login_required
def upload_media(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk)
    User = get_user_model()

    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        
        if form.is_valid():
            media = form.save(commit=False)
            media.session = session

            # Check if a student is logged in
            student = None
            if 'student_id' in request.session:
                student = Student.objects.filter(id=request.session['student_id'], section=session).first()

            if student:
                student_name = student.name
                media.submitted_password = student.password  # Use student's password
            elif request.user.is_staff or request.user.is_superuser:
                # Admin is logged in
                student_name = f"Admin: {request.user.username}"
                media.submitted_password = request.user.media_password  # Assuming admins have a media_password field
            else:
                messages.error(request, 'You do not have permission to upload media to this session.')
                return redirect('session_detail', session_pk=session.pk)

            # Generate the title
            graph_tag = dict(Media.GRAPH_TAG_CHOICES)[form.cleaned_data['graph_tag']]
            variable_tag = dict(Media.VARIABLE_TAG_CHOICES)[form.cleaned_data['variable_tag']]
            media.title = f"{student_name}'s {graph_tag} {variable_tag}"

            media.save()
            messages.success(request, 'Media uploaded successfully.')
            return redirect('session_detail', session_pk=session.pk)
        else:
            messages.error(request, 'There was an error with your form. Please check and try again.')
    else:
        form = MediaForm()

    return render(request, 'video_app/upload_media.html', {'form': form, 'session': session})
   

@login_required
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

from django.db.models import Count
from random import shuffle

from django.db.models import Exists, OuterRef, F, Count
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from random import shuffle
from .models import Session, Media, Student, StudentMediaInteraction

from django.db.models import Value
from django.db.models.expressions import ExpressionWrapper
from django.db.models import BooleanField

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

    # Order by comment count
    medias = medias.annotate(comment_count=Count('comments')).order_by('comment_count')
    
    student = request.session.get('student')
    
    student = None
    if 'student_id' in request.session:
        student = Student.objects.filter(id=request.session['student_id']).first()

    if student:
        medias = medias.annotate(
            has_user_comment=Exists(
                Comment.objects.filter(
                    media=OuterRef('pk'),
                    name=student.name
                )
            )
        )
    else:
        medias = medias.annotate(
            has_user_comment=ExpressionWrapper(Value(False), output_field=BooleanField())
        )
    
    # Randomize order for media with the same comment count
    medias = list(medias)
    current_count = None
    start_index = 0
    for i, media in enumerate(medias):
        if media.comment_count != current_count:
            if i > start_index:
                shuffle(medias[start_index:i])
            current_count = media.comment_count
            start_index = i
    if len(medias) > start_index:
        shuffle(medias[start_index:])

    # Pagination
    paginator = Paginator(medias, 12)  # Show 12 media items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    graph_choices = Media.GRAPH_TAG_CHOICES
    variable_choices = Media.VARIABLE_TAG_CHOICES

    student_instance = None
    if 'student_id' in request.session:
        student_instance = Student.objects.filter(id=request.session['student_id']).first()

    context = {
        'session_instance': session_instance,
        'page_obj': page_obj,
        'graph_choices': graph_choices,
        'variable_choices': variable_choices,
        'selected_graph_tag': graph_tag,
        'selected_variable_tag': variable_tag,
        'student': student_instance,
    }
    return render(request, 'video_app/session_detail.html', context)

from django.contrib.auth import login
from django.contrib.auth import get_user_model

def join_session(request):
    User = get_user_model()
    if request.user.is_staff:
        if request.user.is_superuser:
            sessions = Session.objects.all()
        else:
            sessions = Session.objects.filter(created_by=request.user)
    else:
        sessions = []
    
    if request.method == 'POST':
        student_password = request.POST.get('student_password')
        session_code = request.POST.get('session_code')
        
        if session_code:
            try:
                session_instance = Session.objects.get(session_code=session_code)
                request.session['current_session_id'] = session_instance.id
                request.session['current_session_name'] = session_instance.name
                return redirect('session_detail', session_pk=session_instance.pk)
            except Session.DoesNotExist:
                return render(request, 'video_app/join_session.html', {'error': 'Invalid session code', 'sessions': sessions})
        
        elif student_password:
            try:
                student = Student.objects.get(password=student_password)
                session_instance = student.section
                
                # Create a user account for the student if it doesn't exist
                username = f"student_{student.id}"
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_password(student_password)
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                
                # Log in the student
                login(request, user)
                
                request.session['current_session_id'] = session_instance.id
                request.session['current_session_name'] = session_instance.name
                request.session['student_id'] = student.id
                return redirect('session_detail', session_pk=session_instance.pk)
            except Student.DoesNotExist:
                return render(request, 'video_app/join_session.html', {'error': 'Invalid student password', 'sessions': sessions})
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'video_app/join_session.html', context)



@login_required
def admin_view(request):
    # Get all sessions related to the logged-in admin
    sessions = Session.objects.filter(created_by=request.user)
    
    # Get students related to the logged-in admin with interaction data
    students = Student.objects.filter(admin=request.user).annotate(
        total_votes=Coalesce(Sum(
            Case(
                When(media_interactions__liked_graph=True, then=1),
                When(media_interactions__liked_eye=True, then=1),
                When(media_interactions__liked_read=True, then=1),
                default=0,
                output_field=IntegerField()
            )
        ), 0),
        total_comments=Coalesce(Sum('media_interactions__comment_count'), 0)
    ).select_related('section')

    # Add this to include the teacher's current information
    teacher = request.user
    
    context = {
        'sessions': sessions,
        'students': students,
        'teacher': teacher,
    }
    return render(request, 'video_app/admin_view.html', context)

@login_required
def update_teacher_info(request):
    if request.method == 'POST':
        teacher = request.user
        teacher.district = request.POST.get('district')
        teacher.school = request.POST.get('school')
        teacher.first_name = request.POST.get('first_name')
        teacher.last_name = request.POST.get('last_name')
        teacher.save()
        messages.success(request, 'Teacher information updated successfully.')
    return redirect('admin_view')

def delete_student(request, student_id):
    # Get the student object or return a 404 if not found
    student = get_object_or_404(Student, id=student_id)

    # Ensure the logged-in user is the admin of the student
    if student.admin == request.user:
        student.delete()

    # Redirect back to the admin view after deletion
    return redirect('admin_view')

@login_required
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

@login_required
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

@login_required
def set_media_password(request):
    if request.method == 'POST':
        media_password = request.POST.get('media_password')
        if media_password:
            request.user.media_password = media_password
            request.user.save()
            messages.success(request, 'Media password set successfully.')
        else:
            messages.error(request, 'Please provide a valid media password.')
    return redirect('admin_view')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Media
from .forms import MediaForm  # You'll need to create this form

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Media
from .forms import MediaForm

def edit_media(request, pk):
    media = get_object_or_404(Media, pk=pk)
    
    # Check if the user is authorized to edit this media
    if not request.user.is_staff and request.session.get('device_id') != media.device_id:
        return HttpResponseForbidden("You don't have permission to edit this media.")

    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES, instance=media)
        if form.is_valid():
            media = form.save(commit=False)
            media.graph_tag = form.cleaned_data['graph_tag']
            media.variable_tag = form.cleaned_data['variable_tag']
            media.save()
            return redirect('post_detail', id=media.id)
    else:
        form = MediaForm(instance=media)

    return render(request, 'video_app/edit_media.html', {'form': form, 'media': media})

from django.contrib.auth import logout
from django.shortcuts import redirect

def student_logout(request):
    logout(request)
    return redirect('home')  # or any other appropriate page after logout

@user_passes_test(lambda u: u.is_staff)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    media_id = comment.media.id
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')
    return redirect('post_detail', id=media_id)

from django.shortcuts import render, get_object_or_404
from .models import Student, StudentMediaInteraction, Comment

def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    interactions = StudentMediaInteraction.objects.filter(student=student)
    comments = Comment.objects.filter(student=student)

    context = {
        'student': student,
        'interactions': interactions,
        'comments': comments,
    }
    return render(request, 'video_app/student_detail.html', context)