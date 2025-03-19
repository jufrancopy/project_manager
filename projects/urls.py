from django.urls import path, include
from . import views


urlpatterns = [
    path('register/user/', views.register_user, name='register_user'),
    path('dependency/dashboard/', views.dependency_dashboard, name='dependency_dashboard'),
    # path('submit/', views.submit_project, name='submit_project'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('add/', views.add_project, name='add_project'),

    #Rutas de Gestiòn de Proyectos de usuario con rol de Lider de Proyecto
    path('manager/list/', views.project_list, name='project_list'),  # Mover a una ruta diferente
    path('manager/<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('manager/<int:project_id>/upload_document/', views.upload_document, name='upload_document'),
    path('manager/<int:project_id>/detail', views.project_detail_admin, name='admin_project_detail'),
    path('manager/flujograma/', views.show_flujograma, name='flujograma'),
    path('manager/view-word/<int:document_id>/', views.view_word, name='view_word'),
    path('manager/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    #path('auth-redirect/', views.login_redirect_view, name='login_redirect'),

    path('ckeditor5/', include('django_ckeditor_5.urls')),
]
