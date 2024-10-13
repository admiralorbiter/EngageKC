from django.shortcuts import get_object_or_404, redirect, render
from .models import Student, StudentMediaInteraction, Comment, Media, Session
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentForm
from django.db.models import Count, Sum, F, Case, When, IntegerField
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models.functions import Coalesce


@login_required
def post(request, id):
    media = get_object_or_404(Media, id=id)
    comments = media.comments.filter(parent__isnull=True)
    new_comment = None
    student = None

    if 'student_id' in request.session:
        student = Student.objects.filter(id=request.session['student_id']).first()

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.media = media

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
        'comment_form': comment_form,
        'student': student  # Add the student to the context
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

def nav_sessions(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.user.is_superuser:
            sessions = Session.objects.all()
        else:
            sessions = Session.objects.filter(created_by=request.user)
        return {'nav_sessions': sessions}
    return {'nav_sessions': []}
