from django.urls import path, include
from . import views


urlpatterns = [
    path('register/user/', views.register_user, name='register_user'),
    path('profile/', views.profile_view, name='profile'),
]
