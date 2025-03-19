document.addEventListener("DOMContentLoaded", function () {
    console.log("Script custom_alert.js cargado");

    // Verifica si existe una alerta de error de Bootstrap
    let errorAlertElement = document.querySelector(".alert.alert-danger");
    if (errorAlertElement) {
        let errorMessage = errorAlertElement.innerText.trim(); // Captura el texto dentro de la alerta
        console.log("Mensaje de error:", errorMessage); // Muestra el mensaje de error en consola

        // Elimina la alerta de Bootstrap del DOM
        errorAlertElement.remove();

        // Mostrar alerta con el mensaje de error usando SweetAlert2
        Swal.fire({
            icon: "error",
            title: "¡Error!",
            text: errorMessage,
            confirmButtonText: "Aceptar",
            confirmButtonColor: "#d33",
        });
    } else {
        console.log("No se encontró ningún mensaje de error.");
    }

    // Esta función es llamada cuando el usuario hace clic en el botón de eliminar
    window.confirmDelete = function(url, event) {
        event.preventDefault(); // Prevenir la acción por defecto

        // Mostrar el cuadro de confirmación de SweetAlert2
        Swal.fire({
            title: '¿Estás seguro?',
            text: "¡Este proyecto será eliminado permanentemente!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, eliminarlo',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                // Si el usuario confirma, realizamos la solicitud AJAX para eliminar el proyecto
                fetch(url, {
                    method: 'DELETE', // Usamos el método DELETE
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Asegúrate de enviar el token CSRF
                    },
                })
                .then(response => {
                    if (response.ok) {
                        Swal.fire('¡Eliminado!', 'El proyecto ha sido eliminado.', 'success')
                            .then(() => {
                                // Redirigir a la lista de proyectos
                                window.location.href = '/admin/projects/project/';
                            });
                    } else {
                        Swal.fire('Error', 'Hubo un problema al eliminar el proyecto.', 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Error', 'Hubo un error de red.', 'error');
                });
            }
        });
    };
});
