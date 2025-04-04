# Generated by Django 5.1.6 on 2025-03-20 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('request', 'Solicitud de Elaboración de Proyecto'), ('analysis', 'Análisis de Factibilidad'), ('presentation', 'Presentación para Aprobación'), ('approval', 'Aprobación de Autoridades'), ('development', 'Desarrollo del Proyecto'), ('monitoring', 'Monitoreo y Evaluación')], max_length=50, verbose_name='Tarea')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('completed', models.BooleanField(default=False, verbose_name='Completado')),
                ('deadline', models.DateField(verbose_name='Fecha Límite')),
            ],
            options={
                'verbose_name': 'Tarea',
                'verbose_name_plural': 'Tareas',
            },
        ),
    ]
