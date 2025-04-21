/**
 * Script para gestionar marcas desde un modal
 * Permite crear, eliminar y seleccionar marcas en tiempo real
 */

// Clase para gestionar el modal de marcas
class MarcasModalManager {
    constructor() {
        // Referencias a elementos del DOM
        this.modal = document.getElementById('marcasModal');
        this.formNuevaMarca = document.getElementById('formNuevaMarca');
        this.inputNuevaMarca = document.getElementById('nuevaMarcaNombre');
        this.listaMarcas = document.getElementById('listaMarcas');
        this.buscarInput = document.getElementById('buscarMarcaInput');
        this.selectorMarca = document.querySelector('.select2-marca'); // Selector en el formulario principal
        
        // URLs para las operaciones AJAX (se configuran dinámicamente)
        this.urls = {
            listar: '', // Se asignará desde el HTML
            crear: '',  // Se asignará desde el HTML
            eliminar: '' // Se asignará desde el HTML
        };
        
        // Eventos cuando el modal se abre/cierra
        if (this.modal) {
            this.modal.addEventListener('show.bs.modal', () => this.cargarMarcas());
            this.modal.addEventListener('shown.bs.modal', () => this.inputNuevaMarca.focus());
        }
        
        // Inicializar eventos
        this.inicializarEventos();
    }
    
    // Configurar las URLs para las operaciones AJAX
    setUrls(listar, crear, eliminar) {
        this.urls.listar = listar;
        this.urls.crear = crear;
        this.urls.eliminar = eliminar;
    }
    
    // Inicializar todos los eventos
    inicializarEventos() {
        // Evento para crear nueva marca
        if (this.formNuevaMarca) {
            this.formNuevaMarca.addEventListener('submit', (e) => {
                e.preventDefault();
                this.crearMarca();
            });
        }
        
        // Evento para búsqueda en tiempo real
        if (this.buscarInput) {
            this.buscarInput.addEventListener('input', () => this.filtrarMarcas());
        }
    }
    
    // Cargar todas las marcas desde el servidor
    cargarMarcas() {
        if (!this.urls.listar) {
            console.error('URL para listar marcas no configurada');
            return;
        }
        
        // Mostrar loader
        this.listaMarcas.innerHTML = `
            <div class="list-group-item text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span class="ms-2">Cargando marcas...</span>
            </div>
        `;
        
        // Petición AJAX para obtener marcas
        fetch(this.urls.listar, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.renderizarMarcas(data.marcas);
            } else {
                this.mostrarError('Error al cargar marcas', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.mostrarError('Error de conexión', 'No se pudieron cargar las marcas');
        });
    }
    
    // Renderizar la lista de marcas
    renderizarMarcas(marcas) {
        if (marcas.length === 0) {
            this.listaMarcas.innerHTML = '<div class="list-group-item text-center py-3">No hay marcas disponibles</div>';
            return;
        }
        
        let html = '';
        
        marcas.forEach(marca => {
            const puedeEliminar = marca.productos_count === 0;
            
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center marca-item" 
                     data-id="${marca.id}" 
                     data-nombre="${marca.nombre}">
                    <div>
                        <h6 class="mb-0 marca-nombre">${marca.nombre}</h6>
                        <small class="text-muted">${marca.productos_count} productos</small>
                    </div>
                    <div class="d-flex align-items-center">
                        <button type="button" class="btn btn-sm btn-outline-primary me-2 btn-seleccionar-marca">
                            <i class="fas fa-check"></i> Seleccionar
                        </button>
                        ${puedeEliminar ? `
                            <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar-marca">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : `
                            <button type="button" class="btn btn-sm btn-outline-danger" disabled 
                                    title="No se puede eliminar porque tiene productos asociados">
                                <i class="fas fa-trash"></i>
                            </button>
                        `}
                    </div>
                </div>
            `;
        });
        
        this.listaMarcas.innerHTML = html;
        
        // Añadir eventos a los botones
        this.listaMarcas.querySelectorAll('.btn-seleccionar-marca').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.target.closest('.marca-item');
                const id = item.dataset.id;
                const nombre = item.dataset.nombre;
                this.seleccionarMarca(id, nombre);
            });
        });
        
        this.listaMarcas.querySelectorAll('.btn-eliminar-marca').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.target.closest('.marca-item');
                const id = item.dataset.id;
                const nombre = item.dataset.nombre;
                this.confirmarEliminarMarca(id, nombre);
            });
        });
    }
    
    // Filtrar marcas según texto de búsqueda
    filtrarMarcas() {
        const textoBusqueda = this.buscarInput.value.toLowerCase();
        const items = this.listaMarcas.querySelectorAll('.marca-item');
        
        items.forEach(item => {
            const nombreMarca = item.querySelector('.marca-nombre').textContent.toLowerCase();
            if (nombreMarca.includes(textoBusqueda)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    // Crear una nueva marca
    crearMarca() {
        const nombre = this.inputNuevaMarca.value.trim();
        
        if (!nombre) {
            this.mostrarError('Error', 'El nombre de la marca es requerido');
            return;
        }
        
        // Verificar si ya existe
        const yaExiste = Array.from(this.listaMarcas.querySelectorAll('.marca-nombre'))
            .some(el => el.textContent.toLowerCase() === nombre.toLowerCase());
            
        if (yaExiste) {
            this.mostrarError('La marca ya existe', 'Ya existe una marca con este nombre');
            return;
        }
        
        // Mostrar indicador de carga
        const btnGuardar = document.getElementById('btnGuardarMarca');
        const textoOriginal = btnGuardar.innerHTML;
        btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
        btnGuardar.disabled = true;
        
        // Crear formData para enviar
        const formData = new FormData();
        formData.append('nombre', nombre);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        // Petición AJAX
        fetch(this.urls.crear, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpiar el formulario
                this.inputNuevaMarca.value = '';
                
                // Agregar la nueva marca a la lista y al selector
                this.agregarMarcaALista(data);
                this.agregarMarcaASelector(data);
                
                // Mostrar mensaje de éxito
                this.mostrarExito('Marca creada correctamente');
            } else {
                this.mostrarError('Error al crear marca', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.mostrarError('Error de conexión', 'No se pudo crear la marca');
        })
        .finally(() => {
            // Restaurar botón
            btnGuardar.innerHTML = textoOriginal;
            btnGuardar.disabled = false;
        });
    }
    
    // Agregar una nueva marca a la lista
    agregarMarcaALista(marca) {
        // Si la lista muestra "No hay marcas", limpiarla
        if (this.listaMarcas.querySelector('.list-group-item')?.textContent.includes('No hay marcas')) {
            this.listaMarcas.innerHTML = '';
        }
        
        // Crear el elemento HTML
        const marcaElement = document.createElement('div');
        marcaElement.className = 'list-group-item d-flex justify-content-between align-items-center marca-item';
        marcaElement.dataset.id = marca.id;
        marcaElement.dataset.nombre = marca.nombre;
        
        marcaElement.innerHTML = `
            <div>
                <h6 class="mb-0 marca-nombre">${marca.nombre}</h6>
                <small class="text-muted">0 productos</small>
            </div>
            <div class="d-flex align-items-center">
                <button type="button" class="btn btn-sm btn-outline-primary me-2 btn-seleccionar-marca">
                    <i class="fas fa-check"></i> Seleccionar
                </button>
                <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar-marca">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        // Agregar al principio de la lista con efecto
        this.listaMarcas.prepend(marcaElement);
        
        // Añadir eventos
        marcaElement.querySelector('.btn-seleccionar-marca').addEventListener('click', () => {
            this.seleccionarMarca(marca.id, marca.nombre);
        });
        
        marcaElement.querySelector('.btn-eliminar-marca').addEventListener('click', () => {
            this.confirmarEliminarMarca(marca.id, marca.nombre);
        });
        
        // Destacar con efecto
        marcaElement.style.backgroundColor = '#e8f4ff';
        setTimeout(() => {
            marcaElement.style.transition = 'background-color 1s';
            marcaElement.style.backgroundColor = '';
        }, 50);
    }
    
    // Agregar marca al selector del formulario principal
    agregarMarcaASelector(marca) {
        if (!this.selectorMarca) return;
        
        // Si es un select2, lo gestionamos con su API
        if (typeof $(this.selectorMarca).select2 === 'function') {
            const newOption = new Option(marca.nombre, marca.id, false, false);
            $(this.selectorMarca).append(newOption).trigger('change');
        } else {
            // Para un select normal
            const option = document.createElement('option');
            option.value = marca.id;
            option.text = marca.nombre;
            this.selectorMarca.add(option);
        }
        
        // Disparamos un evento personalizado para notificar a otros componentes
        const event = new CustomEvent('marcaCreada', { detail: marca });
        document.dispatchEvent(event);
    }
    
    // Confirmar eliminación de marca
    confirmarEliminarMarca(id, nombre) {
        if (confirm(`¿Estás seguro de eliminar la marca "${nombre}"?`)) {
            this.eliminarMarca(id, nombre);
        }
    }
    
    // Eliminar marca
    eliminarMarca(id, nombre) {
        // Crear formData para enviar
        const formData = new FormData();
        formData.append('id', id);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        // Mostrar indicador en el elemento
        const marcaItem = this.listaMarcas.querySelector(`.marca-item[data-id="${id}"]`);
        if (marcaItem) {
            marcaItem.style.opacity = '0.5';
            marcaItem.querySelector('.btn-eliminar-marca').disabled = true;
        }
        
        // Petición AJAX
        fetch(this.urls.eliminar, {
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
                if (marcaItem) {
                    marcaItem.style.height = marcaItem.offsetHeight + 'px';
                    marcaItem.style.transition = 'all 0.3s';
                    
                    setTimeout(() => {
                        marcaItem.style.height = '0';
                        marcaItem.style.padding = '0';
                        marcaItem.style.margin = '0';
                        marcaItem.style.overflow = 'hidden';
                        
                        setTimeout(() => {
                            marcaItem.remove();
                            
                            // Si no hay más marcas, mostrar mensaje
                            if (this.listaMarcas.children.length === 0) {
                                this.listaMarcas.innerHTML = '<div class="list-group-item text-center py-3">No hay marcas disponibles</div>';
                            }
                        }, 300);
                    }, 50);
                }
                
                // Eliminar del selector
                this.eliminarMarcaDeSelector(id);
                
                // Mostrar mensaje de éxito
                this.mostrarExito('Marca eliminada correctamente');
                
                // Disparamos un evento personalizado
                const event = new CustomEvent('marcaEliminada', { detail: { id, nombre } });
                document.dispatchEvent(event);
            } else {
                // Restaurar elemento
                if (marcaItem) {
                    marcaItem.style.opacity = '';
                    marcaItem.querySelector('.btn-eliminar-marca').disabled = false;
                }
                
                this.mostrarError('Error al eliminar marca', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Restaurar elemento
            if (marcaItem) {
                marcaItem.style.opacity = '';
                marcaItem.querySelector('.btn-eliminar-marca').disabled = false;
            }
            
            this.mostrarError('Error de conexión', 'No se pudo eliminar la marca');
        });
    }
    
    // Eliminar marca del selector
    eliminarMarcaDeSelector(id) {
        if (!this.selectorMarca) return;
        
        // Si es un select2, lo gestionamos con su API
        if (typeof $(this.selectorMarca).select2 === 'function') {
            const option = $(this.selectorMarca).find(`option[value="${id}"]`);
            if (option.length) {
                option.remove();
                $(this.selectorMarca).trigger('change');
            }
        } else {
            // Para un select normal
            const option = this.selectorMarca.querySelector(`option[value="${id}"]`);
            if (option) {
                option.remove();
            }
        }
    }
    
    // Seleccionar una marca y cerrar el modal
    seleccionarMarca(id, nombre) {
        if (!this.selectorMarca) return;
        
        // Si es un select2, lo gestionamos con su API
        if (typeof $(this.selectorMarca).select2 === 'function') {
            $(this.selectorMarca).val(id).trigger('change');
        } else {
            // Para un select normal
            this.selectorMarca.value = id;
            
            // Disparar evento change
            const event = new Event('change');
            this.selectorMarca.dispatchEvent(event);
        }
        
        // Cerrar el modal
        const bsModal = bootstrap.Modal.getInstance(this.modal);
        if (bsModal) {
            bsModal.hide();
        }
        
        // Mostrar mensaje de éxito
        this.mostrarExito(`Marca "${nombre}" seleccionada`);
    }
    
    // Mostrar mensaje de error
    mostrarError(titulo, mensaje) {
        if (typeof toastr !== 'undefined') {
            toastr.error(mensaje, titulo);
        } else {
            alert(`${titulo}: ${mensaje}`);
        }
    }
    
    // Mostrar mensaje de éxito
    mostrarExito(mensaje) {
        if (typeof toastr !== 'undefined') {
            toastr.success(mensaje);
        } else {
            // No mostramos nada si no hay toastr
        }
    }
}

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    window.marcasManager = new MarcasModalManager();
    
    // Obtener URLs de los atributos data
    const urlsContainer = document.getElementById('marcas-urls');
    if (urlsContainer) {
        window.marcasManager.setUrls(
            urlsContainer.dataset.urlListar,
            urlsContainer.dataset.urlCrear,
            urlsContainer.dataset.urlEliminar
        );
    }
});