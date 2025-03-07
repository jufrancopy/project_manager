from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Project, Task, Document, Dependency, User

class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'leader', 'request_date', 'project_type', 'department', 'dependency',
        'colored_status', 'created_by', 'acciones'
    )
    list_filter = (
        'status', 'request_date', 'project_type', 'department', 'dependency'
    )
    search_fields = (
        'name', 'leader', 'description', 'dependency__name'
    )
    ordering = ('-request_date',)

    def colored_status(self, obj):
        color_map = {
            'request': 'orange',
            'analysis': 'blue',
            'presentation': 'yellow',
            'approval': 'green',
            'development': 'purple',
            'monitoring': 'red',
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )
    colored_status.short_description = 'Estado'

    def acciones(self, obj):
        # URL para agregar una nueva tarea, con el proyecto pre-seleccionado
        add_task_url = reverse('admin:projects_task_add') + f'?project={obj.id}'
        # Botón con ícono de "plus"
        return format_html(
            '<a href="{}" class="button" title="Agregar Tarea">'
            '<i class="fas fa-plus"></i>'  # Ícono de "plus"
            '</a>',
            add_task_url
        )
    acciones.short_description = 'Acciones'
    acciones.allow_tags = True  # Permite renderizar HTML

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_name_display', 'project', 'description', 'completed', 'deadline', 'is_overdue')
    list_filter = ('completed', 'deadline', 'project')
    search_fields = ('project__name', 'description')
    list_editable = ('completed',)
    raw_id_fields = ('project',)

    def get_name_display(self, obj):
        return obj.get_name_display()
    get_name_display.short_description = 'Estado'

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'project', 'uploaded_by', 'upload_date')
    list_filter = ('upload_date', 'project', 'uploaded_by')
    search_fields = ('file', 'project__name', 'uploaded_by__username')
    date_hierarchy = 'upload_date'
    readonly_fields = ('upload_date',)

    def filename(self, obj):
        return obj.file.name.split('/')[-1]
    filename.short_description = 'Nombre del Archivo'

class DependencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'responsible', 'position')
    search_fields = ('name', 'email', 'responsible')

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'dependency')
    list_filter = ('role', 'dependency')
    search_fields = ('username', 'email', 'dependency__name')

# Registro de modelos
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(User, UserAdmin)