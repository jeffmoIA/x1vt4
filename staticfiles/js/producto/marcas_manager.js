// Gestor de marcas con eventos personalizados y actualización en tiempo real
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos DOM
    const marcasContainer = document.getElementById('listaMarcasExistentes'); // Contenedor de la lista de marcas
    const nuevaMarcaInput = document.getElementById('nuevaMarcaNombre');      // Input para nueva marca
    const btnAnadirMarca = document.getElementById('btnAnadirMarca');         // Botón añadir
    const buscadorMarcas = document.getElementById('buscadorMarcas');         // Buscador (opcional)
    const selectorMarca = document.getElementById('id_marca');                // Selector de marcas en el form principal
    
    // URLs para operaciones AJAX (obtenidas desde atributos data-)
    const urlContainer = document.querySelector('[data-url-listar-marcas]');
    const urlListarMarcas = urlContainer ? urlContainer.dataset.urlListarMarcas : null;
    const urlCrearMarca = urlContainer ? urlContainer.dataset.urlCrearMarca : null;
    const urlEliminarMarca = urlContainer ? urlContainer.dataset.urlEliminarMarca : null;
    
    // Evento personalizado para cuando la lista de marcas cambia
    const marcasChangedEvent = new CustomEvent('marcasChanged');
    
    // Verificar que tenemos las URLs necesarias
    if (!urlListarMarcas || !urlCrearMarca || !urlEliminarMarca) {
        console.error('Faltan las URLs para las operaciones AJAX de marcas');
        return;
    }
    
    // Función para cargar marcas desde el servidor
    function cargarMarcas() {
        if (!marcasContainer) return;
        
        // Mostrar indicador de carga
        marcasContainer.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span class="ms-2">Cargando marcas...</span>
            </div>
        `;
        
        // Petición AJAX
        fetch(urlListarMarcas, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al cargar marcas');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                renderizarMarcas(data.marcas);
                // Actualizar también el selector de marcas
                actualizarSelectorMarcas(data.marcas);
            } else {
                throw new Error(data.error || 'Error desconocido');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            marcasContainer.innerHTML = `
                <div class="alert alert-danger">
                    Error al cargar las marcas: ${error.message}
                </div>
            `;
        });
    }
    
    // Función para renderizar la lista de marcas
    function renderizarMarcas(marcas) {
        if (!marcasContainer) return;
        
        if (marcas.length === 0) {
            marcasContainer.innerHTML = '<div class="alert alert-info">No hay marcas registradas</div>';
            return;
        }
        
        // Filtrar marcas si hay un término de búsqueda
        const terminoBusqueda = buscadorMarcas ? buscadorMarcas.value.trim().toLowerCase() : '';
        if (terminoBusqueda) {
            marcas = marcas.filter(marca => 
                marca.nombre.toLowerCase().includes(terminoBusqueda)
            );
        }
        
        // Crear elementos de lista
        const ul = document.createElement('div');
        ul.className = 'list-group';
        
        marcas.forEach(marca => {
            const li = document.createElement('div');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.innerHTML = `
                <span>${marca.nombre}</span>
                <span class="text-muted small">(${marca.productos_count || 0} productos)</span>
                <button type="button" class="btn btn-danger btn-sm eliminar-marca" 
                        data-id="${marca.id}" ${marca.productos_count > 0 ? 'disabled' : ''}>
                    <i class="fas fa-trash"></i>
                </button>
            `;
            ul.appendChild(li);
        });
        
        // Actualizar DOM
        marcasContainer.innerHTML = '';
        marcasContainer.appendChild(ul);
        
        // Configurar botones de eliminar
        ul.querySelectorAll('.eliminar-marca').forEach(btn => {
            btn.addEventListener('click', function() {
                const marcaId = this.dataset.id;
                eliminarMarca(marcaId);
            });
        });
    }
    
    // Función para actualizar el selector de marcas
    function actualizarSelectorMarcas(marcas) {
        if (!selectorMarca) return;
        
        // Guardar el valor seleccionado actual
        const valorSeleccionado = selectorMarca.value;
        
        // Limpiar el selector
        selectorMarca.innerHTML = '';
        
        // Añadir las marcas ordenadas alfabéticamente
        marcas.sort((a, b) => a.nombre.localeCompare(b.nombre))
             .forEach(marca => {
                const option = document.createElement('option');
                option.value = marca.id;
                option.textContent = marca.nombre;
                selectorMarca.appendChild(option);
             });
        
        // Reseleccionar el valor anterior si existe
        if (valorSeleccionado && selectorMarca.querySelector(`option[value="${valorSeleccionado}"]`)) {
            selectorMarca.value = valorSeleccionado;
        }
    }
    
    // Función para crear una nueva marca
    function crearMarca(nombreMarca) {
        // Validación rápida
        if (!nombreMarca.trim()) {
            mostrarError('El nombre de la marca no puede estar vacío');
            return;
        }
        
        // Datos para enviar
        const formData = new FormData();
        formData.append('nombre', nombreMarca.trim());
        formData.append('csrfmiddlewaretoken', getCsrfToken());
        
        // Petición AJAX
        fetch(urlCrearMarca, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpiar campo de entrada
                if (nuevaMarcaInput) nuevaMarcaInput.value = '';
                
                // Mostrar notificación
                mostrarNotificacion('Marca creada correctamente', 'success');
                
                // Actualizar la lista de marcas
                cargarMarcas();
                
                // Disparar evento personalizado
                document.dispatchEvent(marcasChangedEvent);
            } else {
                mostrarError(data.error || 'Error al crear la marca');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarError('Error de conexión al crear la marca');
        });
    }
    
    // Función para eliminar una marca
    function eliminarMarca(marcaId) {
        // Pedir confirmación
        if (!confirm('¿Estás seguro de eliminar esta marca?')) {
            return;
        }
        
        // Datos para enviar
        const formData = new FormData();
        formData.append('id', marcaId);
        formData.append('csrfmiddlewaretoken', getCsrfToken());
        
        // Petición AJAX
        fetch(urlEliminarMarca, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar notificación
                mostrarNotificacion('Marca eliminada correctamente', 'success');
                
                // Actualizar la lista de marcas
                cargarMarcas();
                
                // Disparar evento personalizado
                document.dispatchEvent(marcasChangedEvent);
            } else {
                mostrarError(data.error || 'Error al eliminar la marca');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarError('Error de conexión al eliminar la marca');
        });
    }
    
    // Funciones auxiliares
    function mostrarError(mensaje) {
        const feedbackEl = document.getElementById('nuevaMarcaFeedback');
        if (feedbackEl) {
            feedbackEl.textContent = mensaje;
            feedbackEl.classList.remove('d-none');
            setTimeout(() => {
                feedbackEl.classList.add('d-none');
            }, 3000);
        } else {
            alert(mensaje);
        }
    }
    
    function mostrarNotificacion(mensaje, tipo) {
        // Usar toastr si está disponible
        if (typeof toastr !== 'undefined') {
            toastr[tipo](mensaje);
        }
        // Alternativa simple si toastr no está disponible
        else {
            const notif = document.createElement('div');
            notif.className = `alert alert-${tipo} position-fixed top-0 end-0 m-3`;
            notif.innerHTML = `
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            document.body.appendChild(notif);
            
            setTimeout(() => {
                notif.remove();
            }, 3000);
        }
    }
    
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Configurar eventos cuando el modal se abre - importante para actualizar siempre
    document.getElementById('gestionMarcasModal')?.addEventListener('show.bs.modal', function() {
        cargarMarcas();
    });
    
    // Configurar evento para añadir marca
    if (btnAnadirMarca && nuevaMarcaInput) {
        btnAnadirMarca.addEventListener('click', function() {
            crearMarca(nuevaMarcaInput.value);
        });
        
        // También permitir añadir con Enter
        nuevaMarcaInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                crearMarca(this.value);
            }
        });
    }
    
    // Configurar buscador si existe
    if (buscadorMarcas) {
        buscadorMarcas.addEventListener('input', function() {
            // Recargar para que filtre automáticamente
            cargarMarcas();
        });
    }
    
    // Escuchar eventos personalizados
    document.addEventListener('marcasChanged', function() {
        console.log('Lista de marcas actualizada');
    });
    
    // Carga inicial de marcas
    cargarMarcas();
});