from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import gettext_lazy as _
from .models import User

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


admin.site.register(User, UserAdmin)
