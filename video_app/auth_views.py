from django.contrib.auth import views
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .models import Session, Student

def student_login(request):
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
                return redirect('session', session_pk=session_instance.pk)
            except Session.DoesNotExist:
                return render(request, 'video_app/student_login.html', {'error': 'Invalid session code', 'sessions': sessions})
        
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
                return redirect('session', session_pk=session_instance.pk)
            except Student.DoesNotExist:
                return render(request, 'video_app/student_login.html', {'error': 'Invalid student password', 'sessions': sessions})
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'video_app/student_login.html', context)

def student_logout(request):
    logout(request)
    return redirect('home')  # or any other appropriate page after logout

class AdminLoginView(views.LoginView):
    template_name = 'video_app/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')
    
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
    return redirect('teacher_view')