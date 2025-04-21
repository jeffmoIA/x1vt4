/**
 * Script para gestión de marcas con Select2
 * Implementa toda la funcionalidad relacionada con la selección y gestión de marcas
 */

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Select2 para marcas
    initMarcaSelect2();
    
    // Configurar panel de gestión de marcas
    setupMarcasPanel();
});

/**
 * Inicializa el componente Select2 para selección de marcas
 */
function initMarcaSelect2() {
    const selectElement = $('.select2-marca');
    if (selectElement.length === 0) return;
    
    // Inicializar Select2 con opciones
    selectElement.select2({
        theme: 'bootstrap-5',
        width: '100%',
        language: {
            noResults: "No se encontraron resultados",
            inputTooShort: "Escribe al menos 1 carácter para buscar",
            searching: "Buscando...",
            loadingMore: "Cargando más resultados...",
            errorLoading: "No se pudieron cargar los resultados"
        },
        minimumInputLength: 1,
        tags: true,  // Permite crear nuevas marcas
        createTag: function(params) {
            const term = $.trim(params.term);
            
            // Verificar si ya existe
            let existe = false;
            selectElement.find('option').each(function() {
                if ($(this).text().toLowerCase() === term.toLowerCase()) {
                    existe = true;
                    return false; // Break del loop
                }
            });
            
            if (existe) return null;
            
            // Crear nueva opción de marca
            return {
                id: 'new:' + term,
                text: term + ' (Crear nueva)',
                newTag: true
            };
        }
    }).on('select2:select', function(e) {
        // Si es una nueva marca, crearla
        if (e.params.data.newTag) {
            const nombre = e.params.data.text.replace(' (Crear nueva)', '');
            crearNuevaMarca(nombre, $(this));
        }
    });
}

/**
 * Configura el panel de gestión de marcas existentes
 */
function setupMarcasPanel() {
    // Botón para mostrar/ocultar panel
    const toggleBtn = $('#toggleMarcasPanel');
    if (!toggleBtn.length) return;
    
    // Manejo del panel
    toggleBtn.on('click', function() {
        const panel = $('#marcasPanel');
        panel.slideToggle();
        
        if (panel.is(':visible')) {
            cargarMarcasExistentes();
        }
    });
    
    // Buscar en marcas existentes
    $('#searchMarcas').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        $('#listaMarcasExistentes li').each(function() {
            const text = $(this).find('.marca-nombre').text().toLowerCase();
            $(this).toggle(text.includes(searchTerm));
        });
    });
}

/**
 * Carga la lista de marcas existentes mediante AJAX
 */
function cargarMarcasExistentes() {
    const listaEl = $('#listaMarcasExistentes');
    if (!listaEl.length) return;
    
    // Mostrar indicador de carga
    listaEl.html('<li class="list-group-item text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><span class="ms-2">Cargando marcas...</span></li>');
    
    // Obtener la URL del endpoint (debe estar en el DOM)
    const urlElement = document.querySelector('[data-url-lista-marcas]');
    if (!urlElement) {
        console.error("No se encontró el atributo data-url-lista-marcas");
        listaEl.html('<li class="list-group-item text-danger">Error: URL no configurada</li>');
        return;
    }
    
    const url = urlElement.getAttribute('data-url-lista-marcas');
    
    // Realizar petición AJAX
    $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            if (data.success) {
                renderizarMarcas(data.marcas);
            } else {
                listaEl.html('<li class="list-group-item text-danger">Error: ' + (data.error || 'Desconocido') + '</li>');
            }
        },
        error: function(xhr, status, error) {
            console.error("Error AJAX:", error, xhr.responseText);
            listaEl.html('<li class="list-group-item text-danger">Error de conexión: ' + error + '</li>');
        }
    });
}

/**
 * Renderiza la lista de marcas en el panel
 */
function renderizarMarcas(marcas) {
    const listaEl = $('#listaMarcasExistentes');
    if (!listaEl.length) return;
    
    listaEl.empty();
    
    if (!marcas || marcas.length === 0) {
        listaEl.html('<li class="list-group-item">No hay marcas disponibles</li>');
        return;
    }
    
    // Añadir cada marca a la lista
    marcas.forEach(marca => {
        añadirMarcaALista(marca, listaEl);
    });
}

/**
 * Añade una marca a la lista del panel
 */
function añadirMarcaALista(marca, listaEl) {
    const canDelete = marca.productos_count === 0;
    const li = $(`
        <li class="list-group-item d-flex justify-content-between align-items-center" data-id="${marca.id}">
            <span class="marca-nombre">${marca.nombre}</span>
            <div>
                <span class="badge bg-secondary">${marca.productos_count} productos</span>
                ${canDelete ? 
                    `<button type="button" class="btn btn-sm btn-danger ms-2 btn-eliminar-marca" data-id="${marca.id}">
                        <i class="fas fa-trash"></i>
                    </button>` : 
                    `<button type="button" class="btn btn-sm btn-danger ms-2" disabled title="No se puede eliminar porque tiene productos asociados">
                        <i class="fas fa-trash"></i>
                    </button>`
                }
            </div>
        </li>
    `);
    
    // Añadir evento al botón eliminar
    li.find('.btn-eliminar-marca').on('click', function() {
        const marcaId = $(this).data('id');
        eliminarMarca(marcaId);
    });
    
    // Añadir a la lista
    listaEl.append(li);
}

/**
 * Crea una nueva marca mediante AJAX
 */
function crearNuevaMarca(nombre, selectElement) {
    if (!nombre || !selectElement) return;
    
    // Obtener la URL del endpoint (debe estar en el DOM)
    const urlElement = document.querySelector('[data-url-crear-marca]');
    if (!urlElement) {
        console.error("No se encontró el atributo data-url-crear-marca");
        if (typeof toastr !== 'undefined') {
            toastr.error('Error: URL no configurada');
        } else {
            alert('Error: URL no configurada');
        }
        return;
    }
    
    const url = urlElement.getAttribute('data-url-crear-marca');
    
    // Mostrar indicador de carga
    const placeholder = selectElement.siblings('.select2-container').find('.select2-selection__rendered');
    const textoOriginal = placeholder.text();
    placeholder.html('<i class="fas fa-spinner fa-spin me-1"></i> Creando...');
    
    // Preparar datos del formulario
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Enviar petición AJAX
    $.ajax({
        url: url,
        method: 'POST',
        data: {
            nombre: nombre,
            csrfmiddlewaretoken: csrfToken
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            if (data.success) {
                // Añadir nueva opción al select
                const newOption = new Option(data.nombre, data.id, true, true);
                selectElement.append(newOption).trigger('change');
                
                // Eliminar la opción temporal
                selectElement.find(`option[value="new:${nombre}"]`).remove();
                
                // Actualizar lista si está visible
                if ($('#marcasPanel').is(':visible')) {
                    const nuevaMarca = {
                        id: data.id,
                        nombre: data.nombre,
                        productos_count: 0
                    };
                    
                    const listaEl = $('#listaMarcasExistentes');
                    if (listaEl.length > 0) {
                        añadirMarcaALista(nuevaMarca, listaEl);
                    }
                }
                
                // Mostrar notificación
                if (typeof toastr !== 'undefined') {
                    toastr.success('Marca creada correctamente');
                }
            } else {
                // Mostrar error
                if (typeof toastr !== 'undefined') {
                    toastr.error(data.error || 'Error al crear marca');
                } else {
                    alert(data.error || 'Error al crear marca');
                }
                
                // Restaurar selección anterior
                placeholder.text(textoOriginal);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error AJAX:", error, xhr.responseText);
            
            if (typeof toastr !== 'undefined') {
                toastr.error('Error de conexión: ' + error);
            } else {
                alert('Error de conexión: ' + error);
            }
            
            // Restaurar selección anterior
            placeholder.text(textoOriginal);
        }
    });
}

/**
 * Elimina una marca mediante AJAX
 */
function eliminarMarca(marcaId) {
    if (!marcaId) return;
    
    if (!confirm('¿Estás seguro de eliminar esta marca?')) {
        return;
    }
    
    // Obtener la URL del endpoint (debe estar en el DOM)
    const urlElement = document.querySelector('[data-url-eliminar-marca]');
    if (!urlElement) {
        console.error("No se encontró el atributo data-url-eliminar-marca");
        if (typeof toastr !== 'undefined') {
            toastr.error('Error: URL no configurada');
        } else {
            alert('Error: URL no configurada');
        }
        return;
    }
    
    const url = urlElement.getAttribute('data-url-eliminar-marca');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Enviar petición AJAX
    $.ajax({
        url: url,
        method: 'POST',
        data: {
            id: marcaId,
            csrfmiddlewaretoken: csrfToken
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            if (data.success) {
                // Mostrar notificación
                if (typeof toastr !== 'undefined') {
                    toastr.success('Marca eliminada correctamente');
                }
                
                // Eliminar de la lista
                $(`#listaMarcasExistentes li[data-id="${marcaId}"]`).fadeOut(300, function() {
                    $(this).remove();
                });
                
                // Eliminar del select
                $(`#id_marca option[value="${marcaId}"]`).remove();
                $('.select2-marca').trigger('change');
            } else {
                if (typeof toastr !== 'undefined') {
                    toastr.error(data.error || 'Error al eliminar marca');
                } else {
                    alert(data.error || 'Error al eliminar marca');
                }
            }
        },
        error: function(xhr, status, error) {
            console.error("Error AJAX:", error, xhr.responseText);
            
            if (typeof toastr !== 'undefined') {
                toastr.error('Error de conexión: ' + error);
            } else {
                alert('Error de conexión: ' + error);
            }
        }
    });
}