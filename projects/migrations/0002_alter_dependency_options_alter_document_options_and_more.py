# Generated by Django 5.1.6 on 2025-03-08 19:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dependency',
            options={'verbose_name': 'Dependencia', 'verbose_name_plural': 'Dependencias'},
        ),
        migrations.AlterModelOptions(
            name='document',
            options={'verbose_name': 'Documento', 'verbose_name_plural': 'Documentos'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': 'Projecto', 'verbose_name_plural': 'Proyectos'},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'verbose_name': 'Tarea', 'verbose_name_plural': 'Tareas'},
        ),
        migrations.AddField(
            model_name='project',
            name='assigned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_by_projects', to=settings.AUTH_USER_MODEL, verbose_name='Asignado por'),
        ),
        migrations.AddField(
            model_name='project',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_projects', to=settings.AUTH_USER_MODEL, verbose_name='Asignado a'),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(choices=[('request', 'Solicitud de Elaboración de Proyecto'), ('analysis', 'Análisis de Factibilidad'), ('presentation', 'Presentación para Aprobación'), ('approval', 'Aprobación de Autoridades'), ('development', 'Desarrollo del Proyecto'), ('monitoring', 'Monitoreo y Evaluación')], max_length=50, verbose_name='Tarea'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrador'), ('analyst_leader', 'Analista Líder'), ('analyst_junior', 'Analista Junior'), ('applicant', 'Solicitante')], default='applicant', max_length=50, verbose_name='Rol'),
        ),
    ]
