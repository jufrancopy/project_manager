from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from projects.models import Project
from tasks.models import Task
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required

def dashboard(request):
    if request.user.role == 'analyst_leader':
        projects = Project.objects.filter(dependency=request.user.dependency)
    elif request.user.role == 'analyst_junior':
        projects = Project.objects.filter(assigned_to=request.user)
    else:
        projects = Project.objects.filter(created_by=request.user)

    pending_tasks = Task.objects.filter(project__in=projects, completed=False).count()
    completed_tasks = Task.objects.filter(project__in=projects, completed=True).count()
    total_projects = projects.count()

    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'total_projects': total_projects,
        'is_admin': request.user.is_staff or request.user.is_superuser,
    }
    return render(request, 'projects/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
@user_passes_test(lambda u: u.is_superuser or u.role == 'analyst_leader')
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register_user.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')