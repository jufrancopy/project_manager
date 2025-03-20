from django.contrib import admin

from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_name_display', 'project', 'description', 'completed', 'deadline', 'is_overdue')
    list_filter = ('completed', 'deadline', 'project')
    search_fields = ('project__name', 'description')
    list_editable = ('completed',)
    raw_id_fields = ('project',)

    def get_name_display(self, obj):
        return obj.get_name_display()

    get_name_display.short_description = 'Estado'


admin.site.register(Task, TaskAdmin)


