from django.contrib import admin
from django.contrib.auth.models import Permission
from django.utils.html import format_html
from django.urls import reverse
from .models import Project, Task, Document, Dependency, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'leader', 'request_date', 'project_type', 'department', 'dependency',
        'colored_status', 'created_by', 'assigned_to', 'assigned_by', 'acciones'
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
        add_task_url = reverse('admin:projects_task_add') + f'?project={obj.id}'
        return format_html(
            '<a href="{}" class="button" title="Agregar Tarea">'
            '<i class="fas fa-plus"></i>'
            '</a>',
            add_task_url
        )
    acciones.short_description = 'Acciones'
    acciones.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'analyst_junior':
            # Analistas Junior ven solo los proyectos asignados a ellos
            qs = qs.filter(assigned_to=request.user)
        # Analistas Líder y otros roles ven todos los proyectos
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.filter(role='analyst_junior', dependency=request.user.dependency)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            obj.dependency = request.user.dependency
        if 'assigned_to' in form.changed_data:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)

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

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'dependency')
    list_filter = ('role', 'dependency')
    search_fields = ('username', 'email', 'dependency__name')
    readonly_fields = ('date_joined',)  # Campos de solo lectura
    actions = ['make_analyst']  # Acciones personalizadas

    # Campos personalizados para el formulario de edición
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'role', 'dependency')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Campos personalizados para el formulario de creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'dependency'),
        }),
    )

    def make_analyst(self, request, queryset):
        queryset.update(role='analyst')
    make_analyst.short_description = "Cambiar rol a Analista"

    def save_model(self, request, obj, form, change):
        # Si se está creando un nuevo usuario o cambiando la contraseña
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])  # Genera el hash de la contraseña
        super().save_model(request, obj, form, change)

# Registro de modelos
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(User, UserAdmin)