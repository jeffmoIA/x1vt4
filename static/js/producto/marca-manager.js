/**
 * Gestor simplificado de marcas para productos
 * No requiere dependencias externas como Select2 o Bootstrap
 */
class SimpleMarcaManager {
    constructor(options = {}) {
        // Opciones y configuración
        this.options = Object.assign({
            selectorId: 'id_marca',              // ID del selector de marcas
            createButtonId: 'btn-crear-marca',   // ID del botón para crear marcas
            containerSelector: '.marca-manager', // Selector del contenedor principal
            urls: {
                listar: '',                     // URL para listar marcas (AJAX)
                crear: '',                      // URL para crear marcas (AJAX)
                eliminar: ''                    // URL para eliminar marcas (AJAX)
            }
        }, options);
        
        // Referencias a elementos del DOM
        this.selector = document.getElementById(this.options.selectorId);
        this.container = document.querySelector(this.options.containerSelector);
        this.createButton = document.getElementById(this.options.createButtonId);
        
        // Estado interno
        this.isManagerOpen = false;
        this.csrfToken = this.getCsrfToken();
        
        // Inicialización
        this.init();
    }
    
    // Inicializar el gestor
    init() {
        if (!this.container || !this.selector) {
            console.error('No se encontraron los elementos necesarios para el gestor de marcas');
            return;
        }
        
        // Crear elementos del gestor si no existen
        this.createManagerElements();
        
        // Configurar eventos
        this.setupEvents();
        
        // Cargar las marcas iniciales
        this.loadMarcas();
    }
    
    // Crear los elementos de UI del gestor
    createManagerElements() {
        // Crear panel de gestión de marcas si no existe
        if (!this.container.querySelector('.marca-panel')) {
            const panel = document.createElement('div');
            panel.className = 'marca-panel';
            panel.innerHTML = `
                <div class="marca-form">
                    <div class="input-group">
                        <input type="text" class="form-control" id="new-marca-name" placeholder="Nombre de la marca">
                        <button type="button" class="btn btn-primary" id="save-marca-btn">
                            <i class="fas fa-save"></i> Guardar
                        </button>
                    </div>
                    <div class="form-message mt-2"></div>
                </div>
                <div class="marca-list-container mt-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">Marcas existentes</h6>
                        <input type="text" class="form-control form-control-sm search-marca" 
                               placeholder="Buscar..." style="width: 150px;">
                    </div>
                    <div class="marca-list">
                        <div class="loading-indicator">Cargando marcas...</div>
                    </div>
                </div>
            `;
            
            // Guardar referencias
            this.container.appendChild(panel);
            this.panel = panel;
            this.newMarcaInput = panel.querySelector('#new-marca-name');
            this.saveMarcaButton = panel.querySelector('#save-marca-btn');
            this.marcaListContainer = panel.querySelector('.marca-list');
            this.messageContainer = panel.querySelector('.form-message');
            this.searchInput = panel.querySelector('.search-marca');
            
            // Inicialmente oculto
            panel.style.display = 'none';
        }
    }
    
    // Configurar todos los eventos
    setupEvents() {
        // Evento para mostrar/ocultar panel
        if (this.createButton) {
            this.createButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleManager();
            });
        }
        
        // Evento para guardar marca
        if (this.saveMarcaButton) {
            this.saveMarcaButton.addEventListener('click', () => {
                this.createMarca();
            });
        }
        
        // Evento para buscar en la lista
        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => {
                this.filterMarcas(this.searchInput.value);
            });
        }
        
        // Evento para tecla Enter en el input
        if (this.newMarcaInput) {
            this.newMarcaInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.createMarca();
                }
            });
        }
        
        // Evento para cerrar el panel al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (this.isManagerOpen && 
                !this.container.contains(e.target) && 
                e.target !== this.createButton) {
                this.closeManager();
            }
        });
    }
    
    // Mostrar/ocultar el panel de gestión
    toggleManager() {
        if (this.isManagerOpen) {
            this.closeManager();
        } else {
            this.openManager();
        }
    }
    
    // Abrir el panel
    openManager() {
        if (this.panel) {
            this.panel.style.display = 'block';
            this.isManagerOpen = true;
            
            // Focus en el input
            setTimeout(() => {
                this.newMarcaInput.focus();
            }, 100);
            
            // Si no hay datos cargados, cargarlos
            if (!this.marcaListContainer.querySelector('.marca-item')) {
                this.loadMarcas();
            }
        }
    }
    
    // Cerrar el panel
    closeManager() {
        if (this.panel) {
            this.panel.style.display = 'none';
            this.isManagerOpen = false;
        }
    }
    
    // Cargar marcas desde el servidor
    loadMarcas() {
        if (!this.options.urls.listar) {
            this.showMessage('Error: URL para listar marcas no configurada', 'error');
            return;
        }
        
        this.marcaListContainer.innerHTML = '<div class="loading-indicator">Cargando marcas...</div>';
        
        fetch(this.options.urls.listar, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.renderMarcaList(data.marcas);
            } else {
                this.showMessage('Error al cargar marcas: ' + (data.error || 'Error desconocido'), 'error');
                this.marcaListContainer.innerHTML = '<div class="error-message">Error al cargar marcas</div>';
            }
        })
        .catch(error => {
            console.error('Error al cargar marcas:', error);
            this.marcaListContainer.innerHTML = '<div class="error-message">Error de conexión</div>';
        });
    }
    
    // Renderizar la lista de marcas
    renderMarcaList(marcas) {
        if (!marcas || !marcas.length) {
            this.marcaListContainer.innerHTML = '<div class="empty-message">No hay marcas disponibles</div>';
            return;
        }
        
        let html = '<ul class="list-group">';
        
        marcas.forEach(marca => {
            const canDelete = marca.productos_count === 0;
            
            html += `
                <li class="list-group-item marca-item d-flex justify-content-between align-items-center"
                    data-id="${marca.id}" data-nombre="${marca.nombre}">
                    <div>
                        <span class="marca-nombre">${marca.nombre}</span>
                        <small class="text-muted d-block">${marca.productos_count} productos</small>
                    </div>
                    <div class="marca-actions">
                        <button type="button" class="btn btn-sm btn-primary select-marca-btn">
                            Usar
                        </button>
                        ${canDelete ? `
                            <button type="button" class="btn btn-sm btn-danger delete-marca-btn ms-1">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                    </div>
                </li>
            `;
        });
        
        html += '</ul>';
        this.marcaListContainer.innerHTML = html;
        
        // Añadir eventos a los botones
        this.marcaListContainer.querySelectorAll('.select-marca-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.target.closest('.marca-item');
                const id = item.dataset.id;
                const nombre = item.dataset.nombre;
                this.selectMarca(id, nombre);
            });
        });
        
        this.marcaListContainer.querySelectorAll('.delete-marca-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.target.closest('.marca-item');
                const id = item.dataset.id;
                const nombre = item.dataset.nombre;
                this.confirmDeleteMarca(id, nombre);
            });
        });
    }
    
    // Filtrar marcas según texto de búsqueda
    filterMarcas(searchText) {
        const items = this.marcaListContainer.querySelectorAll('.marca-item');
        const search = searchText.toLowerCase();
        
        items.forEach(item => {
            const nombre = item.querySelector('.marca-nombre').textContent.toLowerCase();
            if (nombre.includes(search)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    // Crear una nueva marca
    createMarca() {
        const nombre = this.newMarcaInput.value.trim();
        
        if (!nombre) {
            this.showMessage('El nombre de la marca es requerido', 'error');
            this.newMarcaInput.focus();
            return;
        }
        
        // Desactivar botón y mostrar indicador
        this.saveMarcaButton.disabled = true;
        this.saveMarcaButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        this.showMessage('', ''); // Limpiar mensajes anteriores
        
        // Crear datos para enviar
        const formData = new FormData();
        formData.append('nombre', nombre);
        formData.append('csrfmiddlewaretoken', this.csrfToken);
        
        // Enviar solicitud AJAX
        fetch(this.options.urls.crear, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpiar el input
                this.newMarcaInput.value = '';
                
                // Mostrar mensaje de éxito
                this.showMessage(`Marca "${data.nombre}" ${data.existed ? 'seleccionada' : 'creada'} correctamente`, 'success');
                
                // Seleccionar la marca en el select
                this.addMarcaToSelect(data.id, data.nombre);
                this.selectMarca(data.id, data.nombre);
                
                // Recargar la lista
                this.loadMarcas();
            } else {
                this.showMessage('Error: ' + (data.error || 'Error desconocido'), 'error');
            }
        })
        .catch(error => {
            console.error('Error al crear marca:', error);
            this.showMessage('Error de conexión', 'error');
        })
        .finally(() => {
            // Restaurar botón
            this.saveMarcaButton.disabled = false;
            this.saveMarcaButton.innerHTML = '<i class="fas fa-save"></i> Guardar';
        });
    }
    
    // Confirmar eliminación de marca
    confirmDeleteMarca(id, nombre) {
        if (confirm(`¿Estás seguro de eliminar la marca "${nombre}"?`)) {
            this.deleteMarca(id, nombre);
        }
    }
    
    // Eliminar una marca
    deleteMarca(id, nombre) {
        const item = this.marcaListContainer.querySelector(`.marca-item[data-id="${id}"]`);
        if (item) {
            item.classList.add('deleting');
            const deleteBtn = item.querySelector('.delete-marca-btn');
            if (deleteBtn) {
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            }
        }
        
        // Crear datos para enviar
        const formData = new FormData();
        formData.append('id', id);
        formData.append('csrfmiddlewaretoken', this.csrfToken);
        
        // Enviar solicitud AJAX
        fetch(this.options.urls.eliminar, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Eliminar del DOM con efecto
                if (item) {
                    item.style.height = item.offsetHeight + 'px';
                    item.style.transition = 'all 0.3s';
                    item.style.overflow = 'hidden';
                    
                    setTimeout(() => {
                        item.style.height = '0';
                        item.style.padding = '0';
                        item.style.margin = '0';
                        
                        setTimeout(() => {
                            item.remove();
                            this.showMessage(`Marca "${nombre}" eliminada correctamente`, 'success');
                            
                            // Si no hay más marcas, mostrar mensaje
                            if (!this.marcaListContainer.querySelector('.marca-item')) {
                                this.marcaListContainer.innerHTML = '<div class="empty-message">No hay marcas disponibles</div>';
                            }
                        }, 300);
                    }, 10);
                }
                
                // Eliminar del select
                this.removeMarcaFromSelect(id);
            } else {
                this.showMessage('Error: ' + (data.error || 'Error desconocido'), 'error');
                
                // Restaurar elemento
                if (item) {
                    item.classList.remove('deleting');
                    const deleteBtn = item.querySelector('.delete-marca-btn');
                    if (deleteBtn) {
                        deleteBtn.disabled = false;
                        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error al eliminar marca:', error);
            this.showMessage('Error de conexión', 'error');
            
            // Restaurar elemento
            if (item) {
                item.classList.remove('deleting');
                const deleteBtn = item.querySelector('.delete-marca-btn');
                if (deleteBtn) {
                    deleteBtn.disabled = false;
                    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                }
            }
        });
    }
    
    // Seleccionar una marca
    selectMarca(id, nombre) {
        if (this.selector) {
            // Establecer la opción seleccionada
            this.selector.value = id;
            
            // Disparar evento change
            const event = new Event('change');
            this.selector.dispatchEvent(event);
            
            // Resaltar la opción en la lista
            const items = this.marcaListContainer.querySelectorAll('.marca-item');
            items.forEach(item => {
                if (item.dataset.id === id) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });
            
            // Mostrar mensaje
            this.showMessage(`Marca "${nombre}" seleccionada`, 'success');
            
            // Cerrar el panel después de seleccionar
            setTimeout(() => {
                this.closeManager();
            }, 1000);
        }
    }
    
    // Añadir marca al selector
    addMarcaToSelect(id, nombre) {
        if (!this.selector) return;
        
        // Verificar si ya existe
        if (!this.selector.querySelector(`option[value="${id}"]`)) {
            const option = document.createElement('option');
            option.value = id;
            option.text = nombre;
            this.selector.add(option);
        }
    }
    
    // Eliminar marca del selector
    removeMarcaFromSelect(id) {
        if (!this.selector) return;
        
        const option = this.selector.querySelector(`option[value="${id}"]`);
        if (option) {
            option.remove();
        }
    }
    
    // Mostrar mensaje en el contenedor
    showMessage(message, type) {
        if (!this.messageContainer) return;
        
        // Limpiar clases anteriores
        this.messageContainer.className = 'form-message mt-2';
        
        if (!message) {
            this.messageContainer.textContent = '';
            return;
        }
        
        // Añadir clase según tipo
        if (type === 'error') {
            this.messageContainer.classList.add('text-danger');
        } else if (type === 'success') {
            this.messageContainer.classList.add('text-success');
        } else if (type === 'info') {
            this.messageContainer.classList.add('text-info');
        }
        
        this.messageContainer.textContent = message;
        
        // Auto-eliminar mensajes de éxito después de unos segundos
        if (type === 'success') {
            setTimeout(() => {
                this.messageContainer.style.transition = 'opacity 1s';
                this.messageContainer.style.opacity = '0';
                
                setTimeout(() => {
                    this.messageContainer.textContent = '';
                    this.messageContainer.style.opacity = '1';
                }, 1000);
            }, 3000);
        }
    }
    
    // Obtener el token CSRF
    getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }
}

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Buscar configuración en un elemento data
    const configEl = document.getElementById('marca-manager-config');
    
    if (configEl) {
        // Crear el gestor con la configuración del elemento
        window.marcaManager = new SimpleMarcaManager({
            selectorId: configEl.dataset.selectorId || 'id_marca',
            createButtonId: configEl.dataset.createButtonId || 'btn-crear-marca',
            containerSelector: configEl.dataset.containerSelector || '.marca-manager',
            urls: {
                listar: configEl.dataset.urlListar,
                crear: configEl.dataset.urlCrear,
                eliminar: configEl.dataset.urlEliminar
            }
        });
    }
});