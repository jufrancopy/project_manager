from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Página de portada
    path('projects/', views.project_list, name='project_list'),  # Mover a una ruta diferente
    path('submit/', views.submit_project, name='submit_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('add_project/', views.add_project, name='add_project'),
    path('project/<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('project/<int:project_id>/upload_document/', views.upload_document, name='upload_document'),
]