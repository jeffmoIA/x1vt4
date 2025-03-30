// Archivo: static/js/producto/marcas_manager.js
// Este script maneja la gestión de marcas para el formulario de producto

document.addEventListener('DOMContentLoaded', function() {
    // Obtener referencias a los elementos del DOM
    const btnGestionarMarcas = document.getElementById('btnGestionarMarcas'); // Botón para abrir el modal
    const nuevaMarcaNombre = document.getElementById('nuevaMarcaNombre'); // Campo para el nombre de nueva marca
    const btnAnadirMarca = document.getElementById('btnAnadirMarca'); // Botón para añadir nueva marca
    const listaMarcasExistentes = document.getElementById('listaMarcasExistentes'); // Contenedor para la lista de marcas
    const selectorMarca = document.getElementById('id_marca'); // Selector de marca en el formulario principal
    
    // Obtener URLs para las operaciones AJAX desde atributos data
    const dataContainer = document.querySelector('[data-url-listar-marcas]');
    if (!dataContainer) {
        console.error('No se encontró el contenedor con las URLs para gestión de marcas');
        return;
    }
    
    const urlListarMarcas = dataContainer.getAttribute('data-url-listar-marcas');
    const urlCrearMarca = dataContainer.getAttribute('data-url-crear-marca');
    const urlEliminarMarca = dataContainer.getAttribute('data-url-eliminar-marca');
    
    // Función para obtener el token CSRF
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Función para cargar la lista de marcas
    function cargarMarcas() {
        fetch(urlListarMarcas)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar marcas');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Limpiar lista actual
                    listaMarcasExistentes.innerHTML = '';
                    
                    // Si no hay marcas, mostrar mensaje
                    if (data.marcas.length === 0) {
                        listaMarcasExistentes.innerHTML = '<div class="text-center p-3">No hay marcas disponibles</div>';
                        return;
                    }
                    
                    // Crear elemento para cada marca
                    data.marcas.forEach(marca => {
                        const marcaItem = document.createElement('div');
                        marcaItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                        marcaItem.innerHTML = `
                            <span>${marca.nombre}</span>
                            <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar-marca" 
                                    data-marca-id="${marca.id}" data-marca-nombre="${marca.nombre}">
                                <i class="fas fa-trash"></i>
                            </button>
                        `;
                        listaMarcasExistentes.appendChild(marcaItem);
                    });
                    
                    // Añadir event listeners a botones de eliminar
                    document.querySelectorAll('.btn-eliminar-marca').forEach(btn => {
                        btn.addEventListener('click', eliminarMarca);
                    });
                } else {
                    console.error('Error:', data.error || 'No se pudieron cargar las marcas');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                listaMarcasExistentes.innerHTML = `
                    <div class="alert alert-danger">
                        Error al cargar marcas: ${error.message}
                    </div>
                `;
            });
    }
    
    // Función para añadir nueva marca
    function anadirMarca() {
        const nombre = nuevaMarcaNombre.value.trim();
        
        // Validación básica
        if (!nombre) {
            mostrarError('El nombre de la marca es obligatorio');
            return;
        }
        
        // Preparar datos para enviar
        const formData = new FormData();
        formData.append('nombre', nombre);
        formData.append('csrfmiddlewaretoken', getCsrfToken());
        
        // Enviar petición AJAX
        fetch(urlCrearMarca, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpiar campo
                nuevaMarcaNombre.value = '';
                // Ocultar error si existe
                ocultarError();
                // Mostrar mensaje de éxito
                mostrarMensaje('success', data.message || 'Marca creada exitosamente');
                // Recargar lista de marcas
                cargarMarcas();
                // Añadir la nueva marca al selector
                const option = document.createElement('option');
                option.value = data.id;
                option.textContent = data.nombre;
                selectorMarca.appendChild(option);
                // Seleccionar la nueva marca
                selectorMarca.value = data.id;
            } else {
                mostrarError(data.error || 'Error al crear la marca');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarError('Error de conexión al crear la marca');
        });
    }
    
    // Función para eliminar marca
    function eliminarMarca(event) {
        const btn = event.currentTarget;
        const marcaId = btn.getAttribute('data-marca-id');
        const marcaNombre = btn.getAttribute('data-marca-nombre');
        
        if (!confirm(`¿Estás seguro de que deseas eliminar la marca "${marcaNombre}"?`)) {
            return;
        }
        
        // Preparar datos para enviar
        const formData = new FormData();
        formData.append('id', marcaId);
        formData.append('csrfmiddlewaretoken', getCsrfToken());
        
        // Enviar petición AJAX
        fetch(urlEliminarMarca, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar mensaje de éxito
                mostrarMensaje('success', data.message || 'Marca eliminada exitosamente');
                // Recargar lista de marcas
                cargarMarcas();
                // Eliminar la marca del selector
                const option = selectorMarca.querySelector(`option[value="${marcaId}"]`);
                if (option) {
                    option.remove();
                }
            } else {
                mostrarMensaje('danger', data.error || 'Error al eliminar la marca');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('danger', 'Error de conexión al eliminar la marca');
        });
    }
    
    // Función para mostrar error en el formulario
    function mostrarError(mensaje) {
        const feedbackElement = document.getElementById('nuevaMarcaFeedback');
        feedbackElement.textContent = mensaje;
        feedbackElement.style.display = 'block';
        nuevaMarcaNombre.classList.add('is-invalid');
    }
    
    // Función para ocultar error
    function ocultarError() {
        const feedbackElement = document.getElementById('nuevaMarcaFeedback');
        feedbackElement.style.display = 'none';
        nuevaMarcaNombre.classList.remove('is-invalid');
    }
    
    // Función para mostrar mensaje general
    function mostrarMensaje(tipo, mensaje) {
        // Crear elemento para el mensaje
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${tipo} alert-dismissible fade show`;
        alertElement.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Añadir al DOM justo después del título del modal
        const modalBody = document.querySelector('.modal-body');
        modalBody.insertBefore(alertElement, modalBody.firstChild);
        
        // Eliminar mensaje después de 3 segundos
        setTimeout(() => {
            alertElement.remove();
        }, 3000);
    }
    
    // Asignar event listeners
    if (btnGestionarMarcas) {
        btnGestionarMarcas.addEventListener('click', function() {
            // Cargar marcas cuando se abre el modal
            cargarMarcas();
        });
    }
    
    if (btnAnadirMarca) {
        btnAnadirMarca.addEventListener('click', anadirMarca);
    }
    
    if (nuevaMarcaNombre) {
        nuevaMarcaNombre.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                anadirMarca();
            }
        });
    }
});