from django.db import models
from django.conf import settings
from projects.models import Project

# Create your models here.
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
            'description': strip_tags(self.description),  # Elimina las etiquetas HTML
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