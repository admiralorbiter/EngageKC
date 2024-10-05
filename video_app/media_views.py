# video_app/media_views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from .forms import MediaForm
from .models import Media, Student, StudentMediaInteraction, Session
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

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
                return redirect('session', session_pk=session.pk)

            # Generate the title
            graph_tag = dict(Media.GRAPH_TAG_CHOICES)[form.cleaned_data['graph_tag']]
            variable_tag = dict(Media.VARIABLE_TAG_CHOICES)[form.cleaned_data['variable_tag']]
            media.title = f"{student_name}'s {graph_tag} {variable_tag}"

            media.save()
            messages.success(request, 'Media uploaded successfully.')
            return redirect('session', session_pk=session.pk)
        else:
            messages.error(request, 'There was an error with your form. Please check and try again.')
    else:
        form = MediaForm()

    return render(request, 'video_app/upload_media.html', {'form': form, 'session': session})
   
@login_required
def delete_media(request, pk):
    # Get the media object or return a 404 if not found
    media = get_object_or_404(Media, pk=pk)

    # Ensure the logged-in user has permission to delete this media
    if request.user.is_staff or media.session.created_by == request.user:
        media.delete()
        messages.success(request, 'Media deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this media.')

    # Redirect back to the session view after deletion
    return redirect('session', session_pk=media.session.pk)



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
            return redirect('post', id=media.id)
    else:
        form = MediaForm(instance=media)

    return render(request, 'video_app/edit_media.html', {'form': form, 'media': media})

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
