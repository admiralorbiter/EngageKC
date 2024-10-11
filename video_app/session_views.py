import csv
import os
from random import shuffle
import random
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Exists, OuterRef, Value, BooleanField, ExpressionWrapper
from engagekc import settings
from .forms import StartSessionForm
from .models import CustomAdmin, Session, Media, Student, Comment, StudentMediaInteraction
from django.core.paginator import Paginator
import json
from django.db.models import Prefetch
from django.http import JsonResponse

def check_section_availability(request):
    section = request.GET.get('section')
    user = request.user
    custom_admin = CustomAdmin.objects.get(id=user.id)
    is_available = not Session.objects.filter(section=section, created_by=custom_admin).exists()
    return JsonResponse({'is_available': is_available})

@transaction.atomic
def start_session(request):
    User = get_user_model()
    user = User.objects.get(username=request.user.username)
    custom_admin, created = CustomAdmin.objects.get_or_create(id=user.id)

    if request.method == 'POST':
        form = StartSessionForm(request.POST)
        if form.is_valid():
            # Extract form data
            section = form.cleaned_data['section']
            num_students = form.cleaned_data['num_students']
            
            # Update teacher information
            custom_admin.district = form.cleaned_data['district']
            custom_admin.school = form.cleaned_data['school']
            custom_admin.first_name = form.cleaned_data['first_name']
            custom_admin.last_name = form.cleaned_data['last_name']
            custom_admin.save()
            
            # Generate the title
            title = f"{custom_admin.last_name}'s Data Deck Fall 2024"
            
            # Check for existing session with the same title and section
            existing_session = Session.objects.filter(name=title, section=section, created_by=custom_admin).first()
            if existing_session:
                messages.error(request, f"A session with the title '{title}' and section '{section}' already exists.")
                return render(request, 'video_app/start_session.html', {'form': form})
            
            # Create the session object
            new_session = Session.objects.create(
                name=title,
                section=section,
                created_by=custom_admin
            )
            
            # Generate students and save them to the database
            generate_users_for_section(new_session, num_students, custom_admin)
            
            messages.success(request, f"Session '{title}' created successfully with {num_students} students.")
            return redirect('teacher_view')
    else:
        initial_data = {
            'district': custom_admin.district,
            'school': custom_admin.school,
            'first_name': custom_admin.first_name,
            'last_name': custom_admin.last_name,
        }
        form = StartSessionForm(initial=initial_data)
    
    return render(request, 'video_app/start_session.html', {'form': form})


def session(request, session_pk):
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
    liked_media = {}
    if 'student_id' in request.session:
        student_instance = Student.objects.filter(id=request.session['student_id']).first()
        if student_instance:
            # Prefetch the interactions for efficiency
            medias = Media.objects.filter(session=session_instance).prefetch_related(
                Prefetch('student_interactions',
                         queryset=StudentMediaInteraction.objects.filter(student=student_instance),
                         to_attr='current_student_interaction')
            )
            
            # Build the liked_media dictionary
            for media in medias:
                interaction = next(iter(media.current_student_interaction), None)
                if interaction:
                    liked_media[str(media.id)] = {
                        'graph': interaction.liked_graph,
                        'eye': interaction.liked_eye,
                        'read': interaction.liked_read
                    }

    context = {
        'session_instance': session_instance,
        'page_obj': page_obj,
        'graph_choices': graph_choices,
        'variable_choices': variable_choices,
        'selected_graph_tag': graph_tag,
        'selected_variable_tag': variable_tag,
        'student': student_instance,
        'liked_media_json': json.dumps(liked_media),  # Add this line
    }
    return render(request, 'video_app/session.html', context)

@login_required
def delete_session(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk)
    session.delete()
    return redirect('teacher_view')

def pause_session(request, session_pk):
    session = get_object_or_404(Session, id=session_pk)
    session.is_paused = not(session.is_paused)
    session.save()
    return redirect('student_login')


@transaction.atomic
def generate_users_for_section(section, num_students, admin):
    """Generates students with Marvel character names and details for a given section, saving them to the database."""
    words_list = load_words()  # Keep this for generating passcodes
    marvel_characters = load_marvel_characters()
    
    generated_students = []
    
    for _ in range(num_students):
        # Pick a unique character that is not already used in the database
        while True:
            character = random.choice(marvel_characters)
            if not Student.objects.filter(name=character['name'], section=section).exists():
                break
        
        # Generate the 2-word passcode
        passcode = generate_passcode(words_list)
        
        # Save the student to the database
        student = Student.objects.create(
            name=character['name'],
            password=passcode,
            section=section,
            admin=admin,
            character_description=character['description'],
            avatar_image_path=character['filename']
        )
        
        generated_students.append(student)
    
    return generated_students


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
    """Generates a 2-word passcode from the loaded word list."""
    return '.'.join(random.sample(words, 2))

def load_marvel_characters():
    """Load Marvel characters from the CSV file."""
    characters = []
    csv_path = os.path.join(settings.BASE_DIR, 'video_app', 'static', 'video_app', 'characters - marvel.csv')
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            characters.append(row)
    return characters