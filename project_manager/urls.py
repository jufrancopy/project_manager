from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import dashboard
from projects.views import CustomLoginView

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('users/', include('users.urls')),
    path('documents/', include('documents.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Configuración para servir archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)