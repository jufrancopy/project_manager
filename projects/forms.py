from django import forms
from django import forms
from django.forms import DateInput
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import strip_tags

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from django_ckeditor_5.widgets import CKEditor5Widget  # Si usas CKEditor 5
from .models import Project, Task, Document, User, Dependency

class ProjectForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label="Descripción",
        required=True,
    )

    class Meta:
        model = Project
        fields = '__all__'
        # widgets = {
        #     'request_date': DateInput(attrs={'type': 'date'}),
        #     'start_date': DateInput(attrs={'type': 'date'}),
        #     'end_date': DateInput(attrs={'type': 'date'}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()  # Inicializa FormHelper
        self.helper.form_method = 'post'  # Método del formulario
        self.helper.form_enctype = 'multipart/form-data'  # Para subida de archivos

        if 'instance' in kwargs and kwargs['instance']:
            stripped_description = strip_tags(kwargs['instance'].description)
            print("stripped_description:", stripped_description)  # Agrega esta línea
            self.fields['description'].initial = stripped_description

        # Identifica los campos de tipo Select o SelectMultiple
        select_fields = [
            field_name for field_name, field in self.fields.items()
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple))
        ]

        # Construye el Layout dinámicamente
        layout_fields = []
        for field_name in self.fields:
            if field_name in select_fields:
                layout_fields.append(Field(field_name, css_class='form-control select2'))
            else:
                layout_fields.append(Field(field_name))

        # Agrega el botón de envío
        layout_fields.append(Submit('submit', 'Guardar', css_class='btn btn-primary'))

        # Asigna el Layout al helper
        self.helper.layout = Layout(*layout_fields)

        if self.instance and self.instance.document:
            # Si hay un archivo subido, muestra un enlace para verlo
            self.fields['document'].help_text = f'Archivo actual: <a href="{self.instance.document.url}">{self.instance.document.name}</a>'

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # Identifica los campos de tipo Select o SelectMultiple
        select_fields = [
            field_name for field_name, field in self.fields.items()
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple))
        ]

        # Construye el Layout dinámicamente
        layout_fields = []
        for field_name in self.fields:
            if field_name in select_fields:
                layout_fields.append(Field(field_name, css_class='form-control select2'))
            else:
                layout_fields.append(Field(field_name))

        # Agrega el botón de envío
        layout_fields.append(Submit('submit', 'Guardar', css_class='btn btn-primary'))

        # Asigna el Layout al helper
        self.helper.layout = Layout(*layout_fields)

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