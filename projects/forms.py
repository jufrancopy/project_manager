from django import forms
from .models import Project, Task, Document, User, Dependency
from django.contrib.auth.forms import UserCreationForm
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Task, User


class ProjectForm(forms.ModelForm):
    document = forms.FileField(required=False)  # Campo para subir documentos

    class Meta:
        model = Project
        fields = ['name', 'leader', 'description', 'request_date', 'project_type', 'department', 'dependency']


class TaskForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label="Descripción",
        required=True,
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'deadline', 'assigned_to']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLES, label="Rol")
    dependency = forms.ModelChoiceField(queryset=Dependency.objects.all(), label="Dependencia", required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'dependency']