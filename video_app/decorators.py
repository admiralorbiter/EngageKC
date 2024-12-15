from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def user_or_observer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated or observer is in session
        if request.user.is_authenticated or 'observer_id' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Please log in to view this content")
            return redirect('admin_login')
    return _wrapped_view 