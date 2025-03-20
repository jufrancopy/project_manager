from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db import models
from projects.models import Project

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

