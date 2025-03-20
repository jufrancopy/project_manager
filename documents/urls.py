from django.urls import path
from . import views

urlpatterns = [
    path('<int:project_id>/upload_document/', views.upload_document, name='upload_document'),
]
