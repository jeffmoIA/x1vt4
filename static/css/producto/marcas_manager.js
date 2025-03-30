/**
 * Gestor exclusivo para la funcionalidad de marcas
 * Trabaja de forma independiente sin interferir con otras funcionalidades
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando gestor de marcas...');
    
    // Referencias a elementos del modal
    const modal = document.getElementById('gestionMarcasModal');
    const btnGestionarMarcas = document.getElementById('btnGestionarMarcas');
    const inputNuevaMarca = document.getElementById('nuevaMarcaNombre');
    const btnAnadirMarca = document.getElementById('btnAnadirMarca');
    const listaMarcas = document.getElementById('listaMarcasExistentes');
    const selectorMarca = document.getElementById('id_marca');
    
    // Detectar si tenemos todos los elementos necesarios
    if (!selectorMarca) {
        console.error('No se encontró el selector de marca (#id_marca)');
        return;
    }
    
    if (!btnGestionarMarcas) {
        console.warn('No se encontró el botón para gestionar marcas (#btnGestionarMarcas)');
    }
    
    // Verificar si estamos en una página de edición de producto
    const isProductoPage = document.querySelector('form[enctype="multipart/form-data"]') !== null;
    if (!isProductoPage) {
        console.log('No estamos en una página de edición de producto, no se inicializa el gestor de marcas');
        return;
    }
    
    // Configurar evento para abrir modal
    if (btnGestionarMarcas) {
        btnGestionarMarcas.addEventListener('click', function() {
            // Si ya existe un modal en el DOM, no hacer nada
            if (document.getElementById('gestionMarcasModal')) {
                return;
            }
            
            // Crear modal si no existe
            crearModal();
            
            // Mostrar modal
            const modalInstance = new bootstrap.Modal(document.getElementById('gestionMarcasModal'));
            modalInstance.show();
            
            // Cargar marcas
            cargarMarcas();
        });
    }
    
    /**
     * Crea el modal de gestión de marcas si no existe
     */
    function crearModal() {
        // Verificar si ya existe
        if (document.getElementById('gestionMarcasModal')) {
            return;
        }
        
        // Crear estructura del modal
        const modalHTML = `
            <div class="modal fade" id="gestionMarcasModal" tabindex="-1" aria-labelledby="gestionMarcasModalLabel">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="gestionMarcasModalLabel">Gestionar Marcas</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Formulario de nueva marca -->
                            <div class="mb-3">
                                <label class="form-label">Añadir nueva marca</label>
                                <div class="input-group">
                                    <input type="text" id="nuevaMarcaNombre" class="form-control" placeholder="Nombre de la marca">
                                    <button type="button" class="btn btn-primary" id="btnAnadirMarca">Añadir</button>
                                </div>
                                <div class="invalid-feedback" id="nuevaMarcaFeedback"></div>
                            </div>
                            
                            <!-- Lista de marcas existentes -->
                            <div>
                                <h6>Marcas existentes</h6>
                                <div id="listaMarcasExistentes" class="list-group">
                                    <div class="text-center p-3">
                                        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                                        <span class="ms-2">Cargando marcas...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Añadir al DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Obtener referencias actualizadas
        const modal = document.getElementById('gestionMarcasModal');
        const inputNuevaMarca = document.getElementById('nuevaMarcaNombre');
        const btnAnadirMarca = document.getElementById('btnAnadirMarca');
        
        // Configurar eventos del nuevo modal
        if (btnAnadirMarca) {
            btnAnadirMarca.addEventListener('click', function() {
                const nombre = inputNuevaMarca.value.trim();
                if (nombre) {
                    crearMarca(nombre);
                } else {
                    mostrarFeedback('Por favor, ingresa un nombre para la marca');
                }
            });
        }
        
        if (inputNuevaMarca) {
            inputNuevaMarca.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    btnAnadirMarca.click();
                }
            });
        }
        
        // Evento cuando se muestra el modal
        modal.addEventListener('shown.bs.modal', function() {
            inputNuevaMarca.focus();
        });
    }
    
    /**
     * Carga las marcas existentes mediante AJAX
     */
    function cargarMarcas() {
        const listaMarcas = document.getElementById('listaMarcasExistentes');
        if (!listaMarcas) return;
        
        // Mostrar loader
        listaMarcas.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span class="ms-2">Cargando marcas...</span>
            </div>
        `;
        
        // Obtener URL de listado
        const url = getUrlListarMarcas();
        if (!url) {
            listaMarcas.innerHTML = '<div class="alert alert-danger">No se pudo determinar la URL para listar marcas</div>';
            return;
        }
        
        // Solicitud AJAX
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                renderizarMarcas(data.marcas);
            } else {
                throw new Error(data.error || 'Error al cargar las marcas');
            }
        })
        .catch(error => {
            console.error('Error al cargar marcas:', error);
            listaMarcas.innerHTML = `
                <div class="alert alert-danger">
                    Error al cargar las marcas: ${error.message}
                </div>
            `;
        });
    }
    
    /**
     * Renderiza la lista de marcas
     */
    function renderizarMarcas(marcas) {
        const listaMarcas = document.getElementById('listaMarcasExistentes');
        if (!listaMarcas) return;
        
        if (!marcas || marcas.length === 0) {
            listaMarcas.innerHTML = '<div class="alert alert-info">No hay marcas disponibles</div>';
            return;
        }
        
        // Crear lista de marcas
        let html = '';
        marcas.forEach(marca => {
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    ${marca.nombre}
                    <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar-marca" 
                            data-id="${marca.id}" data-nombre="${marca.nombre}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        });
        
        listaMarcas.innerHTML = html;
        
        // Configurar botones de eliminar
        listaMarcas.querySelectorAll('.btn-eliminar-marca').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const nombre = this.getAttribute('data-nombre');
                
                if (confirm(`¿Estás seguro de eliminar la marca "${nombre}"?`)) {
                    eliminarMarca(id);
                }
            });
        });
    }
    
    /**
     * Crea una nueva marca
     */
    function crearMarca(nombre) {
        const btnAnadirMarca = document.getElementById('btnAnadirMarca');
        const inputNuevaMarca = document.getElementById('nuevaMarcaNombre');
        
        if (!btnAnadirMarca || !inputNuevaMarca) return;
        
        // Obtener URL para crear marca
        const url = getUrlCrearMarca();
        if (!url) {
            mostrarFeedback('No se pudo determinar la URL para crear marcas');
            return;
        }
        
        // Mostrar estado de carga
        btnAnadirMarca.disabled = true;
        btnAnadirMarca.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Añadiendo...';
        
        // Obtener token CSRF
        const csrftoken = getCsrfToken();
        
        // Solicitud AJAX
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `nombre=${encodeURIComponent(nombre)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Restaurar botón
            btnAnadirMarca.disabled = false;
            btnAnadirMarca.innerHTML = 'Añadir';
            
            if (data.success) {
                // Limpiar input
                inputNuevaMarca.value = '';
                
                // Mostrar mensaje
                mostrarNotificacion('success', data.message || 'Marca creada correctamente');
                
                // Añadir al selector
                if (selectorMarca) {
                    const option = new Option(data.nombre, data.id, true, true);
                    selectorMarca.add(option);
                }
                
                // Recargar lista
                cargarMarcas();
            } else {
                mostrarFeedback(data.error || 'Error al crear la marca');
            }
        })
        .catch(error => {
            console.error('Error al crear marca:', error);
            
            // Restaurar botón
            btnAnadirMarca.disabled = false;
            btnAnadirMarca.innerHTML = 'Añadir';
            
            // Mostrar error
            mostrarFeedback('Error al crear la marca: ' + error.message);
        });
    }
    
    /**
     * Elimina una marca
     */
    function eliminarMarca(id) {
        // Obtener URL para eliminar marca
        const url = getUrlEliminarMarca();
        if (!url) {
            mostrarNotificacion('error', 'No se pudo determinar la URL para eliminar marcas');
            return;
        }
        
        // Mostrar loader en la lista
        const listaMarcas = document.getElementById('listaMarcasExistentes');
        if (listaMarcas) {
            listaMarcas.innerHTML = `
                <div class="text-center p-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                    <span class="ms-2">Eliminando marca...</span>
                </div>
            `;
        }
        
        // Obtener token CSRF
        const csrftoken = getCsrfToken();
        
        // Solicitud AJAX
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `id=${encodeURIComponent(id)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Mostrar mensaje
                mostrarNotificacion('success', data.message || 'Marca eliminada correctamente');
                
                // Eliminar del selector
                if (selectorMarca) {
                    const option = selectorMarca.querySelector(`option[value="${id}"]`);
                    if (option) {
                        // Si es la seleccionada actualmente, seleccionar otra
                        if (option.selected && selectorMarca.options.length > 1) {
                            const newIndex = option.index === 0 ? 1 : option.index - 1;
                            selectorMarca.selectedIndex = newIndex;
                        }
                        selectorMarca.removeChild(option);
                    }
                }
                
                // Recargar lista
                cargarMarcas();
            } else {
                mostrarNotificacion('error', data.error || 'Error al eliminar la marca');
                cargarMarcas();
            }
        })
        .catch(error => {
            console.error('Error al eliminar marca:', error);
            mostrarNotificacion('error', 'Error al eliminar la marca: ' + error.message);
            cargarMarcas();
        });
    }
    
    /**
     * Muestra feedback de error en el input
     */
    function mostrarFeedback(mensaje) {
        const feedback = document.getElementById('nuevaMarcaFeedback');
        const input = document.getElementById('nuevaMarcaNombre');
        
        if (feedback && input) {
            feedback.textContent = mensaje;
            feedback.style.display = 'block';
            input.classList.add('is-invalid');
            
            setTimeout(() => {
                feedback.style.display = 'none';
                input.classList.remove('is-invalid');
            }, 5000);
        }
    }
    
    /**
     * Muestra una notificación
     */
    function mostrarNotificacion(tipo, mensaje) {
        // Usar toastr si está disponible
        if (typeof toastr !== 'undefined') {
            toastr[tipo](mensaje);
            return;
        }
        
        // Alternativa: alert simple
        alert(mensaje);
    }
    
    /**
     * Obtiene el token CSRF
     */
    function getCsrfToken() {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return csrfInput ? csrfInput.value : '';
    }
    
    /**
     * Obtiene la URL para listar marcas
     */
    function getUrlListarMarcas() {
        // Intentar extraer URL de los atributos de datos
        const urlElement = document.querySelector('[data-url-listar-marcas]');
        if (urlElement && urlElement.getAttribute('data-url-listar-marcas')) {
            return urlElement.getAttribute('data-url-listar-marcas');
        }
        
        // Intentar construir URL desde el contexto actual
        const currentPath = window.location.pathname;
        if (currentPath.includes('/catalogo/admin/productos/')) {
            return '/catalogo/admin/marcas/listar/';
        }
        
        // Derivar de scripts cargados
        const scripts = document.querySelectorAll('script[src*="catalogo"]');
        if (scripts.length > 0) {
            const scriptSrc = scripts[0].getAttribute('src');
            const basePath = scriptSrc.split('/static/')[0];
            return `${basePath}/catalogo/admin/marcas/listar/`;
        }
        
        // Valor por defecto
        return '/catalogo/admin/marcas/listar/';
    }
    
    /**
     * Obtiene la URL para crear marcas
     */
    function getUrlCrearMarca() {
        // Intentar extraer URL de los atributos de datos
        const urlElement = document.querySelector('[data-url-crear-marca]');
        if (urlElement && urlElement.getAttribute('data-url-crear-marca')) {
            return urlElement.getAttribute('data-url-crear-marca');
        }
        
        // Intentar construir URL desde el contexto actual
        const currentPath = window.location.pathname;
        if (currentPath.includes('/catalogo/admin/productos/')) {
            return '/catalogo/admin/marcas/crear/';
        }
        
        // Derivar de scripts cargados
        const scripts = document.querySelectorAll('script[src*="catalogo"]');
        if (scripts.length > 0) {
            const scriptSrc = scripts[0].getAttribute('src');
            const basePath = scriptSrc.split('/static/')[0];
            return `${basePath}/catalogo/admin/marcas/crear/`;
        }
        
        // Valor por defecto
        return '/catalogo/admin/marcas/crear/';
    }
    
    /**
     * Obtiene la URL para eliminar marcas
     */
    function getUrlEliminarMarca() {
        // Intentar extraer URL de los atributos de datos
        const urlElement = document.querySelector('[data-url-eliminar-marca]');
        if (urlElement && urlElement.getAttribute('data-url-eliminar-marca')) {
            return urlElement.getAttribute('data-url-eliminar-marca');
        }
        
        // Intentar construir URL desde el contexto actual
        const currentPath = window.location.pathname;
        if (currentPath.includes('/catalogo/admin/productos/')) {
            return '/catalogo/admin/marcas/eliminar/';
        }
        
        // Derivar de scripts cargados
        const scripts = document.querySelectorAll('script[src*="catalogo"]');
        if (scripts.length > 0) {
            const scriptSrc = scripts[0].getAttribute('src');
            const basePath = scriptSrc.split('/static/')[0];
            return `${basePath}/catalogo/admin/marcas/eliminar/`;
        }
        
        // Valor por defecto
        return '/catalogo/admin/marcas/eliminar/';
    }
});