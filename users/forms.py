from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User
from dependencies.models import Dependency

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLES, label="Rol")
    dependency = forms.ModelChoiceField(queryset=Dependency.objects.all(), label="Dependencia", required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'dependency']