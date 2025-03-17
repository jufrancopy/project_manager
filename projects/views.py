from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from projects.models import Project, Task, Document, User
from projects.forms import ProjectForm, TaskForm, DocumentForm, UserRegisterForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import re
import unicodedata
from bs4 import BeautifulSoup
import mammoth
from projects.models import Document
from django.views.generic.edit import CreateView


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
    if request.user.role == 'analyst_junior':  # Restringir solo a analyst_junior
        raise PermissionDenied("Los Analistas Junior no pueden agregar proyectos.")

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
                messages.success(request, "Tarea agregada exitosamente.")
                return redirect('project_detail', project_id=project.id)
            except Exception as e:
                messages.error(request, f"Error al agregar la tarea: {str(e)}")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
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

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'  # Plantilla personalizada
    redirect_authenticated_user = True  # Redirige a usuarios ya autenticados

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser:
            return reverse_lazy('admin:index')  # Redirige al panel de administración de Django
        elif user.role == 'analyst_leader':
            return reverse_lazy('project_list')  # Redirige al dashboard del analyst_leader
        elif user.role == 'applicant':
            return reverse_lazy('dependency_dashboard')  # Redirige al dashboard del solicitante
        elif user.role == 'analyst_junior':
            return reverse_lazy('project_list')  # Redirige a la lista de proyectos
        else:
            return reverse_lazy('home')  # Redirección predeterminada

@login_required
def project_list(request):
    if request.user.role != 'analyst_leader':
         raise PermissionDenied("No tienes permiso para acceder a esta vista.")

    # Obtener los proyectos asignados al analyst_leader
    projects = Project.objects.all()

    return render(request, 'projects/project_list.html', {'projects': projects})

def show_flujograma(request):
    return render(request, 'projects/flujograma.html')

def view_word(request, document_id):
    # Obtén el documento de la base de datos
    document = get_object_or_404(Document, id=document_id)
    print(f"Documento encontrado: {document.filename}")  # Depuración

    # Lee el archivo Word y conviértelo a HTML
    with document.file.open('rb') as docx_file:
        result = mammoth.convert_to_html(docx_file)
        content = result.value  # HTML generado
        print(f"HTML generado: {content}")  # Depuración

    # Agregar IDs a los títulos y subtítulos
    content, headings = add_ids_to_headings(content)
    print(f"Títulos extraídos: {headings}")  # Depuración

    # Pasa el contenido y los títulos a la plantilla
    return render(request, 'projects/view_word.html', {'content': content, 'headings': headings, 'document': document})


def normalize_id(text):
    # Normaliza el texto (elimina tildes)
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Convierte a minúsculas y reemplaza caracteres no alfanuméricos con guiones
    id_text = re.sub(r'[^a-zA-Z0-9]+', '-', normalized_text.lower())
    # Elimina guiones al inicio o final
    return id_text.strip('-')

def add_ids_to_headings(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = []
    used_ids = set()  # Para evitar IDs duplicados

    # Buscar elementos <strong> y <h1> a <h6>
    for tag in soup.find_all(['strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        # Genera un ID basado en el texto del título
        base_id = normalize_id(tag.text.strip())
        heading_id = base_id

        # Si el ID ya existe, agrega un sufijo numérico
        counter = 1
        while heading_id in used_ids:
            heading_id = f"{base_id}-{counter}"
            counter += 1

        used_ids.add(heading_id)  # Registrar el ID como usado
        tag['id'] = heading_id  # Agrega el ID al título

        # Guarda el título en la lista
        headings.append({
            'text': tag.text.strip(),
            'id': heading_id,
            'level': tag.name  # Nivel del título (etiqueta HTML)
        })
        print(f"Added ID '{heading_id}' to heading: {tag.text.strip()}")  # Depuración

    return str(soup), headings