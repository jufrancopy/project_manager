from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from .models import Project
from .forms import ProjectForm
from users.models import User

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm  # Usa el formulario personalizado
    list_display = (
        'name', 'leader', 'request_date', 'project_type', 'department', 'dependency',
        'colored_status', 'created_by', 'assigned_to', 'assigned_by', 'acciones'
    )
    list_filter = (
        'status', 'request_date', 'project_type', 'department', 'dependency'
    )
    search_fields = (
        'name', 'leader', 'description', 'dependency__name'
    )
    ordering = ('-request_date',)

    class Media:
        js = ('admin/js/sweetalert2@11.js', 'admin/js/custom_alert.js')  # Incluir SweetAlert2 y nuestro script

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
        add_task_url = reverse('admin:tasks_task_add') + f'?project={obj.id}'
        delete_url = reverse('delete_project', args=[obj.id])
        return format_html(
            '<a href="{}" class="btn-circle bg-btn-blue" title="Agregar Tarea">'
            '<i class="fas fa-tasks text-white"></i>'
            '</a> '
            '<a href="#" class="btn-circle" title="Eliminar Proyecto" onclick="confirmDelete(\'{}\', event)">'
            '<i class="fas fa-trash text-white"></i>'
            '</a>',
            add_task_url,
            delete_url
        )

    acciones.short_description = 'Acciones'
    acciones.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'analyst_junior':
            # Analistas Junior ven solo los proyectos asignados a ellos
            qs = qs.filter(assigned_to=request.user)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.filter(role='analyst_junior', dependency=request.user.dependency)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # 🚀 Acceder a los valores del formulario
        print("📌 Nombre del Proyecto:", obj.name)
        print("👤 Líder del Proyecto:", obj.leader)
        print("📝 Descripción:", obj.description)
        print("📅 Fecha de Solicitud:", obj.request_date)
        print("📌 Tipo de Proyecto:", obj.project_type)
        print("🏢 Departamento:", obj.department)
        print("🏛️ Dependencia Solicitante:", obj.dependency)
        print("📊 Estado del Proyecto:", obj.status)
        print("📂 Documento del Proyecto:", obj.document if obj.document else "No subido")
        print("👨‍💼 Creado por:", obj.created_by)
        print("🎯 Asignado a:", obj.assigned_to if obj.assigned_to else "No asignado")
        print("🔄 Asignado por:", obj.assigned_by if obj.assigned_by else "No asignado")
        print("🚀 Fecha de Inicio:", obj.start_date if obj.start_date else "No definida")
        print("🏁 Fecha de Finalización:", obj.end_date if obj.end_date else "No definida")

        if not obj.pk:
            obj.created_by = request.user
            if not request.user.dependency:
                messages.error(request,
                               "El usuario no tiene una dependencia asignada y es obligatoria para crear un proyecto.")
                return  # Detenemos el guardado y no llamamos `super().save_model(...)`

        if 'assigned_to' in form.changed_data:
            obj.assigned_by = request.user

        super().save_model(request, obj, form, change)

admin.site.register(Project, ProjectAdmin)
