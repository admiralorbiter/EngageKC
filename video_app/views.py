from .forms import CommentForm
from .forms import LoginForm, StartSessionForm
from .models import CustomAdmin, Media, Session, Student
from .models import CustomAdmin, Session
from .models import Media
from .models import Media, Comment
from .models import Media, Student, StudentMediaInteraction
from .models import Session, Media, Student, StudentMediaInteraction
from .models import Student, StudentMediaInteraction, Comment
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import BooleanField
from django.db.models import Count
from django.db.models import Exists, OuterRef, F, Count
from django.db.models import F
from django.db.models import Sum, Count, F, Case, When, IntegerField
from django.db.models import Value
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from engagekc import settings
from io import BytesIO
from random import shuffle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import base64
import csv
import openpyxl
import os
import random


@login_required
def post(request, id):
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
                return redirect('post', id=media.id)

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
            return redirect('post', id=media.id)
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

    return render(request, 'video_app/post.html', context)


# Add this function to update comment count
def update_comment_count(student, media):
    interaction, created = StudentMediaInteraction.objects.get_or_create(
        student=student,
        media=media
    )
    interaction.comment_count += 1
    interaction.save()


def index(request):
    return render(request, 'video_app/index.html')

@login_required
def teacher_view(request):
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
    
    # Get top 10 media items for leaderboard
    media_leaderboard = Media.objects.annotate(
        total_votes=Sum(F('graph_likes') + F('eye_likes') + F('read_likes')),
        total_comments=Count('comments')
    ).order_by('-total_votes')[:10]  # Get top 10 media items

    context = {
        'sessions': sessions,
        'students': students,
        'teacher': teacher,
        'media_leaderboard': media_leaderboard,
    }
    return render(request, 'video_app/teacher_view.html', context)

def delete_student(request, student_id):
    # Get the student object or return a 404 if not found
    student = get_object_or_404(Student, id=student_id)

    # Ensure the logged-in user is the admin of the student
    if student.admin == request.user:
        student.delete()

    # Redirect back to the admin view after deletion
    return redirect('teacher_view')

@login_required
def download_students(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    students = Student.objects.filter(admin=request.user).select_related('section')
    
    # Calculate how many cards can fit on a page
    card_width = 3.5 * inch
    card_height = 2 * inch
    cols = 2
    rows = 4
    
    data = []
    for i in range(0, len(students), cols * rows):
        page_students = students[i:i + cols * rows]
        page_data = []
        for j in range(rows):
            row_data = []
            for k in range(cols):
                index = j * cols + k
                if index < len(page_students):
                    student = page_students[index]
                    card_data = [
                        [f"Name: {student.name}", "Your Name:"],
                        [f"Section: {student.section.name}", ""],
                        [f"Password: {student.password}", ""],
                        ["", ""],  # Empty row for spacing
                        ["--------------------", "--------------------"],
                        [f"Password: {student.password}", ""],
                        ["", ""]  # Empty row to prevent cutting off
                    ]
                    row_data.append(Table(card_data, colWidths=[1.75*inch, 1.75*inch], rowHeights=[0.3*inch, 0.25*inch, 0.25*inch, 0.5*inch, 0.2*inch, 0.3*inch, 0.2*inch]))
                else:
                    row_data.append("")
            page_data.append(row_data)
        data.extend(page_data)
    
    table = Table(data, colWidths=[card_width] * cols, rowHeights=[card_height] * rows)
    
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 4), (-1, 5), 'CENTER'),  # Center the divider line and bottom password
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ])
    table.setStyle(style)
    
    elements = [table]
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_credentials.pdf"'
    
    return response


def filter_media(request, session_pk):
    tags = request.GET.getlist('tags')
    
    # Construct the URL with the selected tags
    url = reverse('session', kwargs={'session_pk': session_pk})
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
    return redirect('teacher_view')

@user_passes_test(lambda u: u.is_staff)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    media_id = comment.media.id
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')
    return redirect('post', id=media_id)

def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    interactions = StudentMediaInteraction.objects.filter(student=student)
    comments = Comment.objects.filter(student=student)
    
    # Get the student's session
    session = student.section
    
    # Get posts made by the student
    student_posts = Media.objects.filter(session=session, submitted_password=student.password)

    # Calculate feedback stats
    graph_count = interactions.filter(liked_graph=True).count()
    eye_count = interactions.filter(liked_eye=True).count()
    read_count = interactions.filter(liked_read=True).count()

    context = {
        'student': student,
        'interactions': interactions,
        'comments': comments,
        'student_posts': student_posts,
        'graph_count': graph_count,
        'eye_count': eye_count,
        'read_count': read_count,
    }
    return render(request, 'video_app/student_detail.html', context)

def nav_sessions(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.user.is_superuser:
            sessions = Session.objects.all()
        else:
            sessions = Session.objects.filter(created_by=request.user)
        return {'nav_sessions': sessions}
    return {'nav_sessions': []}