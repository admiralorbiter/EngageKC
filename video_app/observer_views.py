from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from .models import Session, Observer

def observer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        observer_id = request.session.get('observer_id')
        if not observer_id:
            messages.error(request, "Please log in as an observer")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@observer_required
def observer_dashboard(request):
    try:
        observer = Observer.objects.get(id=request.session['observer_id'])
        available_sessions = Session.objects.filter(
            created_by__district=observer.district
        ).select_related('created_by').order_by('created_by__last_name', 'section')
        
        context = {
            'observer_name': observer.name,
            'observer_district': observer.district,
            'available_sessions': available_sessions
        }
        
        # Refresh the session
        request.session.modified = True
        
        return render(request, 'video_app/observer_dashboard.html', context)
    except Observer.DoesNotExist:
        # Clear the invalid session
        request.session.flush()
        messages.error(request, "Observer not found")
        return redirect('admin_login') 

def observer_logout(request):
    if 'observer_id' in request.session:
        request.session.flush()  # This clears all session data
    messages.success(request, "Successfully logged out")
    return redirect('admin_login')