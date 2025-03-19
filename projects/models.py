import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import format_html

from dependencies.models import Dependency

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
    dependency = models.ForeignKey(Dependency, on_delete=models.CASCADE, verbose_name="Dependencia Solicitante", null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='request', verbose_name="Estado del Proyecto")
    document = models.FileField(
        upload_to='project_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'])],
        verbose_name="Documento del Proyecto",
        null=True,
        blank=True
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

    def save(self, *args, **kwargs):
        # Guarda el proyecto primero
        super().save(*args, **kwargs)

        # Si se subió un archivo, crea un registro en Document
        if self.document:
            Document.objects.create(
                project=self,  # Relaciona el documento con este proyecto
                file=self.document,  # Asigna el archivo subido
                uploaded_by=self.created_by  # Asigna el usuario que creó el proyecto
            )
            super().save(*args, **kwargs)  # Guarda el proyecto nuevamente

    def delete(self, *args, **kwargs):
        # Elimina el archivo asociado al campo `document` en Project
        if self.document:
            if os.path.isfile(self.document.path):
                os.remove(self.document.path)

        # Elimina los archivos asociados en el modelo Document
        for document in self.documents.all():
            if os.path.isfile(document.file.path):
                os.remove(document.file.path)
            document.delete()  # Elimina el registro de Document

        # Llama al método delete() de la clase padre para eliminar el proyecto
        super().delete(*args, **kwargs)
    class Meta:
        verbose_name = "Projecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.name

