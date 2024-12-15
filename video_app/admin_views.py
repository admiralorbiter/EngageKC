from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from video_app.models import Observer

@login_required
def admin_dashboard(request):
    return render(request, 'video_app/admin_dashboard.html')

@login_required
def deactivate_observer(request, observer_id):
    observer = Observer.objects.get(id=observer_id)
    observer.is_active = False
    observer.save()
    return redirect('admin_dashboard')
