from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Dependency

class DependencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'responsible', 'position')
    search_fields = ('name', 'email', 'responsible')

admin.site.register(Dependency, DependencyAdmin)

