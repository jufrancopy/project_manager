from django.contrib.auth.models import AbstractUser
from django.db import models

from dependencies.models import Dependency


# Create your models here.
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