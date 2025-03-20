from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Project
from documents.forms import DocumentForm

def upload_document(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.project = project
                document.uploaded_by = request.user
                document.save()
                messages.success(request, "Documento subido exitosamente.")
                return redirect('project_detail', project_id=project.id)
            except Exception as e:
                messages.error(request, f"Error al subir el documento: {str(e)}")
    else:
        form = DocumentForm()
    return render(request, 'projects/upload_document.html', {'form': form, 'project': project})


from django.shortcuts import render

# Create your views here.
