from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ObserverAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require observer authentication
        exempt_urls = [
            reverse('admin_login'),
            reverse('home'),
            reverse('student_login'),
            # Add other public URLs as needed
        ]

        # Check if this is an observer-only page
        if (request.path.startswith('/observer/') and 
            request.path not in exempt_urls and 
            'observer_id' not in request.session):
            messages.error(request, "Please log in as an observer to access this page")
            return redirect('admin_login')

        response = self.get_response(request)
        return response