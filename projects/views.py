from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Task, Document
from .forms import ProjectForm, TaskForm, DocumentForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView



# Lista todos los proyectos
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})

# Muestra los detalles de un proyecto, sus tareas y documentos
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    return render(request, 'projects/project_detail.html', {'project': project, 'tasks': tasks})


# Agrega un nuevo proyecto
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                project = form.save(commit=False)
                project.created_by = request.user  # Asigna el usuario actual como creador
                project.dependency = request.user.dependency  # Asigna la dependencia del usuario
                project.save()

                # Verifica si el usuario subió un archivo y créalo en el modelo Document
                document_file = request.FILES.get("document")
                if document_file:
                    Document.objects.create(
                        project=project,
                        file=document_file,
                        uploaded_by=request.user
                    )

                # Enviar correo de confirmación
                send_mail(
                    'Solicitud de Proyecto Recibida',
                    f'Su proyecto "{project.name}" ha sido recibido. Estado actual: {project.get_status_display()}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],  # Enviar al correo del usuario
                    fail_silently=False,
                )

                messages.success(request, "Proyecto creado exitosamente.")
                return redirect("project_list")
            except Exception as e:
                messages.error(request, f"Error al crear el proyecto: {str(e)}")
    else:
        form = ProjectForm()

    return render(request, "projects/add_project.html", {"form": form})

# Agrega una tarea a un proyecto específico
from django.contrib import messages

def add_task(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = form.save(commit=False)
                task.project = project
                task.save()
                messages.success(request, "Tarea agregada exitosamente.")
                return redirect('project_detail', pk=project.id)
            except Exception as e:
                messages.error(request, f"Error al agregar la tarea: {str(e)}")
    else:
        form = TaskForm()
    return render(request, 'projects/add_task.html', {'form': form, 'project': project})

# Sube un documento a un proyecto específico
from django.contrib import messages

def upload_document(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.project = project
                document.uploaded_by = request.user
                document.save()
                messages.success(request, "Documento subido exitosamente.")
                return redirect('project_detail', pk=project.id)
            except Exception as e:
                messages.error(request, f"Error al subir el documento: {str(e)}")
    else:
        form = DocumentForm()
    return render(request, 'projects/upload_document.html', {'form': form, 'project': project})

def dashboard(request):
    # Obtener el número de tareas pendientes y completadas
    if request.user.is_staff or request.user.is_superuser:
        pending_tasks = Task.objects.filter(completed=False).count()
        completed_tasks = Task.objects.filter(completed=True).count()
        total_projects = Project.objects.count()
    else:
        pending_tasks = Task.objects.filter(project__created_by=request.user, completed=False).count()
        completed_tasks = Task.objects.filter(project__created_by=request.user, completed=True).count()
        total_projects = Project.objects.filter(created_by=request.user).count()

    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'total_projects': total_projects,
        'is_admin': request.user.is_staff or request.user.is_superuser,
    }
    return render(request, 'projects/dashboard.html', context)


from django.core.exceptions import PermissionDenied


def change_project_status(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Solo los analistas pueden cambiar el estado
    if request.user.role != 'analyst':
        raise PermissionDenied("No tienes permiso para cambiar el estado de este proyecto.")

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Project.STATUS_CHOICES).keys():  # Verifica que el estado sea válido
            project.status = new_status
            project.save()

            # Enviar correo de notificación
            send_mail(
                f'Estado del Proyecto Actualizado: {project.name}',
                f'El estado de su proyecto "{project.name}" ha cambiado a: {project.get_status_display()}.',
                settings.DEFAULT_FROM_EMAIL,
                [project.created_by.email],  # Enviar al creador del proyecto
                fail_silently=False,
            )

            messages.success(request, f"Estado del proyecto actualizado a: {project.get_status_display()}.")
            return redirect('project_detail', pk=project.id)
        else:
            messages.error(request, "Estado no válido.")
    return render(request, 'projects/change_project_status.html', {'project': project})


def submit_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            # Enviar notificación por correo
            send_mail(
                'Solicitud de Proyecto Recibida',
                f'Su proyecto "{project.name}" ha sido recibido. Estado actual: {project.get_status_display()}.',
                settings.DEFAULT_FROM_EMAIL,
                [project.dependency.email],
                fail_silently=False,
            )
            return redirect('project_submitted')
    else:
        form = ProjectForm()
    return render(request, 'projects/submit_project.html', {'form': form})


class ChangeProjectStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    fields = ['status']
    template_name = 'projects/change_project_status.html'

    def test_func(self):
        # Solo los analistas pueden cambiar el estado
        return self.request.user.role == 'analyst'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Enviar correo de notificación
        send_mail(
            f'Estado del Proyecto Actualizado: {self.object.name}',
            f'El estado de su proyecto "{self.object.name}" ha cambiado a: {self.object.get_status_display()}.',
            settings.DEFAULT_FROM_EMAIL,
            [self.object.created_by.email],
            fail_silently=False,
        )
        messages.success(self.request, f"Estado del proyecto actualizado a: {self.object.get_status_display()}.")
        return response