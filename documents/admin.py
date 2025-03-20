from django.contrib import admin

from django.urls import reverse
from django.utils.html import format_html

from documents.models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'project', 'uploaded_by', 'upload_date', 'view_word_link')
    list_filter = ('upload_date', 'project', 'uploaded_by')
    search_fields = ('file', 'project__name', 'uploaded_by__username')
    date_hierarchy = 'upload_date'
    readonly_fields = ('upload_date',)

    def view_word_link(self, obj):
        if obj.file:
            try:
                url = reverse('view_word', kwargs={'document_id': obj.id})  # Asegúrate de usar el nombre correcto
                return format_html('<a href="{}">Ver documento</a>', url)
            except Exception as e:
                return f"Error en URL: {e}"
        return "No hay documento"

    view_word_link.short_description = 'Ver Documento'

admin.site.register(Document, DocumentAdmin)
