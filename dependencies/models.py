
from django.db import models

class Dependency(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre de la Dependencia")
    email = models.EmailField(verbose_name="Correo Electrónico")
    responsible = models.CharField(max_length=200, verbose_name="Responsable")
    position = models.CharField(max_length=200, verbose_name="Cargo del Responsable")
    additional_info = models.TextField(verbose_name="Información Adicional", blank=True, null=True)

    class Meta:
        verbose_name = "Dependencia"
        verbose_name_plural = "Dependencias"
        ordering = ["name"]

    def __str__(self):
        return self.name