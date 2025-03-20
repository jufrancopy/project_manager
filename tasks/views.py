from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from tasks.forms import TaskForm

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from projects.models import Project
from .models import Task
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


# Agrega una tarea a un proyecto específico
def add_task(request, project_id):
    if request.user.role != 'analyst':
        raise PermissionDenied("Solo los analistas pueden agregar tareas.")

    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                task.project = project
                task.save()
                messages.success(request, "Tarea agregada exitosamente.")
                return redirect('project_detail', project_id=project.id)
            except Exception as e:
                messages.error(request, f"Error al agregar la tarea: {str(e)}")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = TaskForm()

    return render(request, 'projects/add_task.html', {'form': form, 'project': project})

@csrf_exempt  # Solo para desarrollo, usa CSRF token en producción
def toggle_completed(request, task_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            completed = data.get('completed')
            task = get_object_or_404(Task, pk=task_id)
            task.completed = completed
            task.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})