from django.shortcuts import redirect
from django.urls import reverse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('auth'))

        if request.user.role == 'applicant' and not request.path.startswith('/applicant/'):
            return redirect(reverse('applicant_dashboard'))

        if request.user.role == 'analyst' and not request.path.startswith('/analyst/'):
            return redirect(reverse('analyst_dashboard'))

        if request.user.role == 'admin' and not request.path.startswith('/admin/'):
            return redirect(reverse('admin_dashboard'))

        return self.get_response(request)