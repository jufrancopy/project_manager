from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Task

class TaskForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'),
        label="Descripción",
        required=True,
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'completed', 'deadline', 'assigned_to']
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

