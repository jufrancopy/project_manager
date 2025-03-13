from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from projects.views import dashboard
from projects.views import CustomLoginView

urlpatterns = [
    path('', dashboard, name='dashboard'),  # Ahora accesible desde la raíz
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('projects/', include('projects.urls')),  # Incluye las URLs de la aplicación "projects"
]

# Configuración para servir archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)