from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from .models import Project, Task, Document, User
from .forms import ProjectForm, TaskForm, DocumentForm, UserRegisterForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
import logging



# Lista todos los proyectos
def project_list(request):
    print(f"Usuario: {request.user}, Rol: {request.user.role}")
    if request.user.role == 'applicant':
        projects = Project.objects.filter(dependency=request.user.dependency)
    elif request.user.role == 'analyst_junior':
        projects = Project.objects.filter(assigned_to=request.user)
    else:
        projects = Project.objects.all()
    print(f"Proyectos encontrados: {projects.count()}")
    return render(request, 'projects/project_list.html', {'projects': projects})

# Muestra los detalles de un proyecto, sus tareas y documentos
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    documents = Document.objects.filter(project=project)
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'documents': documents,
    })

# Agrega un nuevo proyecto
def add_project(request):
    if request.user.role != 'applicant':
        raise PermissionDenied("Solo los solicitantes pueden agregar proyectos.")

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

                # Enviar correo a la dependencia
                send_mail(
                    'Solicitud de Proyecto Recibida',
                    f'Su proyecto "{project.name}" ha sido recibido. Estado actual: {project.get_status_display()}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [project.dependency.email],  # Correo de la dependencia
                    fail_silently=False,
                )

                # Mensaje de éxito
                messages.success(request, "Proyecto creado exitosamente.")
                return redirect("project_list")  # Redirigir a la lista de proyectos

            except Exception as e:
                # Mensaje de error si algo falla
                messages.error(request, f"Error al crear el proyecto: {str(e)}")
    else:
        form = ProjectForm()  # Mostrar el formulario vacío si no es una solicitud POST

    return render(request, "projects/add_project.html", {"form": form})

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

                # Notificar a la dependencia sobre la nueva tarea
                send_mail(
                    f'Nueva Tarea para el Proyecto: {project.name}',
                    f'Se ha agregado una nueva tarea al proyecto "{project.name}". Estado: {task.get_name_display()}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [project.dependency.email],  # Correo de la dependencia
                    fail_silently=False,
                )

                messages.success(request, "Tarea agregada exitosamente.")
                return redirect('project_detail', project_id=project.id)
            except Exception as e:
                messages.error(request, f"Error al agregar la tarea: {str(e)}")
    else:
        form = TaskForm()
    return render(request, 'projects/add_task.html', {'form': form, 'project': project})

# Sube un documento a un proyecto específico
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
                return redirect('project_detail', project_id=project.id)
            except Exception as e:
                messages.error(request, f"Error al subir el documento: {str(e)}")
    else:
        form = DocumentForm()
    return render(request, 'projects/upload_document.html', {'form': form, 'project': project})

# Panel de control
def dashboard(request):
    if request.user.role == 'analyst_leader':
        # Los Analistas Líder ven todos los proyectos de su dependencia
        projects = Project.objects.filter(dependency=request.user.dependency)
    elif request.user.role == 'analyst_junior':
        # Los Analistas Junior ven solo los proyectos asignados a ellos
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

# Cambia el estado de un proyecto
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
            return redirect('project_detail', project_id=project.id)
        else:
            messages.error(request, "Estado no válido.")
    return render(request, 'projects/change_project_status.html', {'project': project})

# Vista basada en clases para cambiar el estado del proyecto
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

@user_passes_test(lambda u: u.is_superuser)  # Solo el superusuario puede acceder
@user_passes_test(lambda u: u.is_superuser or u.role == 'analyst')  # Superusuarios y analistas
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
def dependency_dashboard(request):
    if request.user.role != 'applicant':
        raise PermissionDenied("Solo los solicitantes pueden acceder a esta vista.")

    # Obtener los proyectos de la dependencia del usuario
    projects = Project.objects.filter(dependency=request.user.dependency)
    return render(request, 'dependency_dashboard.html', {'projects': projects})


@staff_member_required
def project_detail_admin(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('admin_project_detail', project_id=project.id)
    else:
        form = TaskForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'form': form,
    })

logger = logging.getLogger(__name__)  # Configurar el log

@login_required
def redirect_based_on_role(request):
    user = request.user
    logger.debug(f"Redirigiendo usuario: {user.username} con rol: {user.role}")

    if user.role == "applicant":
        return redirect("dependency_dashboard")  # Asegúrate de que esta URL está definida
    elif user.role == "analyst":
        return redirect("dashboard")
    elif user.role == "analys|t_leader":
        return redirect("leader_dashboard")  # Asegúrate de que esta URL existe
    elif user.is_superuser:
        return redirect("admin:index")  # Redirige al panel de administración
    else:
        logger.warning(f"Usuario {user.username} con rol desconocido: {user.role}")
        return redirect("home")  # Redirigir a una página por defecto

@login_required
def leader_dashboard(request):
    if request.user.is_authenticated:
        print("Usuario autenticado:", request.user)
    else:
        print("El usuario no está autenticado")
    return render(request, 'projects/leader_dashboard.html', {})