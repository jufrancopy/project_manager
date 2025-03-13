from django.utils.html import format_html
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db import models
from django.core.mail import send_mail

class Dependency(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre de la Dependencia")
    email = models.EmailField(verbose_name="Correo Electrónico")
    responsible = models.CharField(max_length=200, verbose_name="Responsable")
    position = models.CharField(max_length=200, verbose_name="Cargo del Responsable")
    additional_info = models.TextField(verbose_name="Información Adicional", blank=True, null=True)

    class Meta:
        verbose_name = "Dependencia"
        verbose_name_plural = "Dependencias"

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('analyst_leader', 'Analista Líder'),
        ('analyst_junior', 'Analista Junior'),
        ('applicant', 'Solicitante'),
    ]

    role = models.CharField(max_length=50, choices=ROLES, default='applicant', verbose_name="Rol")
    dependency = models.ForeignKey(Dependency, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Dependencia")

    @property
    def is_analyst_leader(self):
        return self.role == 'analyst_leader'

    verbose_name = "Usuario"
    verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username

class Project(models.Model):
    PROJECT_TYPES = [
        ('infra', 'Infraestructura'),
        ('med', 'Medicamentos e Insumos'),
        ('tic', 'TIC'),
        ('electro', 'Electromedicina'),
        ('econ', 'Prestaciones Económicas'),
        ('medic', 'Prestaciones Médicas'),
        ('talent', 'Talentos Humanos'),
    ]

    DEPARTMENTS = [
        ('asuncion', 'Asunción'),
        ('concepcion', 'Concepción'),
        ('san_pedro', 'San Pedro'),
        ('cordillera', 'Cordillera'),
        ('guaira', 'Guairá'),
        ('caaguazu', 'Caaguazú'),
        ('caazapa', 'Caazapá'),
        ('itapua', 'Itapúa'),
        ('misiones', 'Misiones'),
        ('paraguari', 'Paraguarí'),
        ('alto_parana', 'Alto Paraná'),
        ('central', 'Central'),
        ('ñeembucu', 'Ñeembucú'),
        ('amambay', 'Amambay'),
        ('canindeyu', 'Canindeyú'),
        ('presidente_hayes', 'Presidente Hayes'),
        ('boqueron', 'Boquerón'),
        ('alto_paraguay', 'Alto Paraguay'),
        ('nacional', 'Nacional')  # Opción adicional
    ]

    STATUS_CHOICES = [
        ('request', 'Solicitud de Elaboración de Proyecto'),
        ('analysis', 'Análisis de Factibilidad'),
        ('presentation', 'Presentación para Aprobación'),
        ('approval', 'Aprobación de Autoridades'),
        ('development', 'Desarrollo del Proyecto'),
        ('monitoring', 'Monitoreo y Evaluación'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre del Proyecto")
    leader = models.CharField(max_length=200, verbose_name="Líder del Proyecto")
    description = models.TextField(verbose_name="Descripción")
    request_date = models.DateField(verbose_name="Fecha de Solicitud")
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES, verbose_name="Tipo de Proyecto")
    department = models.CharField(max_length=50, choices=DEPARTMENTS, verbose_name="Departamento")
    dependency = models.ForeignKey(Dependency, on_delete=models.CASCADE, verbose_name="Dependencia Solicitante")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='request', verbose_name="Estado del Proyecto")
    document = models.FileField(
        upload_to='project_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'])],
        verbose_name="Documento del Proyecto"
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Creado por")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_projects',
        verbose_name="Asignado a"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_by_projects',
        verbose_name="Asignado por"
    )

    start_date = models.DateField(verbose_name="Fecha de Inicio", null=True, blank=True)
    end_date = models.DateField(verbose_name="Fecha de Finalización", null=True, blank=True)

    def colored_status(self):
        color_map = {
            'request': 'orange',
            'analysis': 'blue',
            'presentation': 'yellow',
            'approval': 'green',
            'development': 'purple',
            'monitoring': 'red',
        }
        color = color_map.get(self.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.get_status_display()
        )
    colored_status.short_description = 'Estado'

    class Meta:
        verbose_name = "Projecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('request', 'Solicitud de Elaboración de Proyecto'),
        ('analysis', 'Análisis de Factibilidad'),
        ('presentation', 'Presentación para Aprobación'),
        ('approval', 'Aprobación de Autoridades'),
        ('development', 'Desarrollo del Proyecto'),
        ('monitoring', 'Monitoreo y Evaluación'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Proyecto")
    name = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="Tarea")
    description = models.TextField(verbose_name="Descripción")
    completed = models.BooleanField(default=False, verbose_name="Completado")
    deadline = models.DateField(verbose_name="Fecha Límite")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Relación con el modelo de usuario
        on_delete=models.SET_NULL,  # Si el usuario es eliminado, el campo se establece como NULL
        null=True,  # Permite valores nulos en la base de datos
        blank=True,  # Permite que el campo esté vacío en los formularios
        verbose_name="Asignado a"
    )

    def get_name_display(self):
        """Devuelve el nombre legible del estado basado en STATUS_CHOICES."""
        return dict(self.STATUS_CHOICES).get(self.name, "Sin estado")

    def is_overdue(self):
        return self.deadline < timezone.now().date() if self.deadline else False
    is_overdue.boolean = True
    is_overdue.short_description = '¿Atrasada?'

    def notify_status_change(self):
        # Renderizar la plantilla HTML
        context = {
            'project_name': self.project.name,
            'new_status': self.get_name_display(),
            'description': self.description,
            'deadline': self.deadline,
            'completed': self.completed,
        }
        html_message = render_to_string('emails/status_change_notification.html', context)

        # Crear el correo
        subject = f"Cambio de estado en el proyecto {self.project.name}"
        email = EmailMessage(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.project.dependency.email],  # Enviar correo a la dependencia
        )
        email.content_subtype = "html"  # Indicar que el contenido es HTML
        email.send(fail_silently=False)

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Verificar si es nueva tarea
        if is_new:
            self.notify_status_change()
        else:
            old_task = Task.objects.get(pk=self.pk)
            if old_task.name != self.name:
                self.notify_status_change()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def __str__(self):
        return self.get_name_display()

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Proyecto",related_name="documents")
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        verbose_name="Documento"
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]
    filename.short_description = 'Nombre del Archivo'

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self):
        return self.file.name

