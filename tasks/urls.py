from django.urls import path
from . import views


urlpatterns = [
    path('<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('<int:task_id>/toggle_completed/', views.toggle_completed, name='toggle_completed'),

]
