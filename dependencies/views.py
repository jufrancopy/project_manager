from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from projects.models import Project


def dependency_dashboard(request):
    if request.user.role != 'applicant':
        raise PermissionDenied("Solo los solicitantes pueden acceder a esta vista.")

    # Obtener los proyectos de la dependencia del usuario
    projects = Project.objects.filter(dependency=request.user.dependency)
    return render(request, 'dependency_dashboard.html', {'projects': projects})
