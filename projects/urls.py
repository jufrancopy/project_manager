from django.urls import path, include
from . import views

urlpatterns = [
    path('register/user/', views.register_user, name='register_user'),
    path('dependency/dashboard/', views.dependency_dashboard, name='dependency_dashboard'),
    path('projects/', views.project_list, name='project_list'),  # Mover a una ruta diferente
    #path('submit/', views.submit_project, name='submit_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('add/project/', views.add_project, name='add_project'),
    path('project/<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('project/<int:project_id>/upload_document/', views.upload_document, name='upload_document'),
    path('admin/project/<int:project_id>/', views.project_detail_admin, name='admin_project_detail'),
    path('analyst_leader_dashboard/', views.analyst_leader_dashboard, name='analyst_leader_dashboard'),

    path('ckeditor5/', include('django_ckeditor_5.urls')),
]