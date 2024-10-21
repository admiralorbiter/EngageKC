from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Student, StudentMediaInteraction, Comment, Media
from django.contrib.auth.decorators import login_required
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os
from django.conf import settings
import csv

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
                        [f"Hour: {student.section.section}", ""],
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

    # Calculate row heights dynamically based on the number of rows in data
    row_heights = [card_height] * len(data)

    table = Table(data, colWidths=[card_width] * cols, rowHeights=row_heights)
    
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

def character_gallery(request):
    character_sets = []
    characters_dir = os.path.join(settings.BASE_DIR, 'video_app', 'static', 'video_app', 'images', 'characters')
    
    for character_set in os.listdir(characters_dir):
        set_path = os.path.join(characters_dir, character_set)
        if os.path.isdir(set_path):
            images = []
            for root, dirs, files in os.walk(set_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        relative_path = os.path.relpath(os.path.join(root, file), characters_dir)
                        images.append(relative_path)
            if images:
                character_sets.append({
                    'name': character_set,
                    'images': images
                })
    
    return render(request, 'video_app/character_gallery.html', {'character_sets': character_sets})
