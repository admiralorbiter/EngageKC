from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from video_app.models import Observer, CustomAdmin
from django.contrib.auth.hashers import make_password

@login_required
def admin_dashboard(request):
    if not isinstance(request.user, CustomAdmin):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')  # or wherever you want to redirect non-admin users

    if request.method == 'POST':
        # Handle observer creation
        name = request.POST.get('name')
        email = request.POST.get('email')
        district = request.POST.get('district')
        password = request.POST.get('password')

        try:
            # Create observer with hashed password
            Observer.objects.create(
                name=name,
                email=email,
                district=district,
                password=make_password(password),
                created_by=request.user,
                is_active=True
            )
            messages.success(request, f"Observer {name} created successfully!")
        except Exception as e:
            messages.error(request, f"Error creating observer: {str(e)}")
        
        return redirect('admin_dashboard')

    # Get all observers for display
    observers = Observer.objects.filter(created_by=request.user)
    
    # Get unique districts from CustomAdmin model
    districts = CustomAdmin.objects.values_list('district', flat=True).distinct()

    context = {
        'observers': observers,
        'districts': districts,
    }
    
    return render(request, 'video_app/admin_dashboard.html', context)

@login_required
def deactivate_observer(request, observer_id):
    if not isinstance(request.user, CustomAdmin):
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')

    try:
        observer = Observer.objects.get(id=observer_id, created_by=request.user)
        observer.is_active = not observer.is_active
        observer.save()
        status = "activated" if observer.is_active else "deactivated"
        messages.success(request, f"Observer {observer.name} has been {status}.")
    except Observer.DoesNotExist:
        messages.error(request, "Observer not found.")
    
    return redirect('admin_dashboard')
