from django.urls import path, include
from . import views

urlpatterns = [
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('add/', views.add_project, name='add_project'),
    path('list/', views.project_list, name='project_list'),  # Mover a una ruta diferente
    path('<int:project_id>/detail', views.project_detail_admin, name='admin_project_detail'),
    path('flujograma/', views.show_flujograma, name='flujograma'),
    path('view-word/<int:document_id>/', views.view_word, name='view_word'),
    path('<int:project_id>/delete/', views.delete_project, name='delete_project'),
]
