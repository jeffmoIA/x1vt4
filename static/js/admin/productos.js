/**
 * productos.js - Gestión de tablas de productos para administradores
 * Este script maneja la inicialización segura de DataTables para la vista de admin de productos.
 */

// Función de inicialización segura (ejecutada cuando el DOM está listo)
document.addEventListener('DOMContentLoaded', function() {
    console.log("Inicializando módulo de administración de productos...");
    
    // Iniciar con DataTables
    initDataTable();
});

// Variables globales
let productosTable = null;
let filtroCategoria = '';
let filtroMarca = '';
let filtroDisponibilidad = '';

/**
 * Inicializa DataTables con verificación de dependencias
 */
function initDataTable() {
    console.log("Inicializando DataTable...");
    
    // Verificar si jQuery está disponible
    if (typeof jQuery === 'undefined') {
        console.error('jQuery no está disponible. La tabla de productos no funcionará correctamente.');
        mostrarError('jQuery no está disponible. Por favor, recargue la página.');
        return;
    }
    
    const $ = jQuery;
    
    // Verificar si DataTables está disponible
    if (typeof $.fn.DataTable === 'undefined') {
        console.error('La biblioteca DataTables no está disponible.');
        // Intentar cargar DataTables dinámicamente
        cargarDataTables();
        return;
    }
    
    iniciarTablaProductos($);
}

/**
 * Intenta cargar DataTables dinámicamente
 */
function cargarDataTables() {
    console.log("Intentando cargar DataTables dinámicamente...");
    
    const $ = jQuery;
    
    // Mensaje de carga
    mostrarInfo("Cargando recursos necesarios...");
    
    // Cargar CSS de DataTables
    const linkCSS = document.createElement('link');
    linkCSS.rel = 'stylesheet';
    linkCSS.href = 'https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css';
    document.head.appendChild(linkCSS);
    
    // Cargar JavaScript de DataTables
    const scriptDT = document.createElement('script');
    scriptDT.src = 'https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js';
    scriptDT.onload = function() {
        // Después de cargar DataTables core, cargar la integración con Bootstrap
        const scriptDTBS = document.createElement('script');
        scriptDTBS.src = 'https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js';
        scriptDTBS.onload = function() {
            console.log("DataTables cargado correctamente de forma dinámica");
            iniciarTablaProductos($);
        };
        scriptDTBS.onerror = function() {
            console.error("Error al cargar DataTables Bootstrap integration");
            mostrarError("No se pudo cargar DataTables. Por favor, recargue la página.");
        };
        document.body.appendChild(scriptDTBS);
    };
    scriptDT.onerror = function() {
        console.error("Error al cargar DataTables core");
        mostrarError("No se pudo cargar DataTables. Por favor, recargue la página.");
    };
    document.body.appendChild(scriptDT);
}

/**
 * Inicia la tabla de productos con DataTables
 */
function iniciarTablaProductos($) {
    try {
        const tablaElement = document.getElementById('productos-table');
        if (!tablaElement) {
            console.error("No se encontró la tabla de productos");
            return;
        }

        console.log("Iniciando tabla de productos con DataTables");
        
        // Inicializar DataTable con configuración
        productosTable = $(tablaElement).DataTable({
            // Configuración para procesamiento en servidor
            processing: true,
            serverSide: true,
            ajax: {
                url: productosDataUrl, // Esta variable debe estar definida en la plantilla
                type: "POST",
                // Incluir el token CSRF en la solicitud
                headers: {
                    "X-CSRFToken": getCookie('csrftoken')
                },
                // Añadir datos de filtros y timestamp
                data: function(d) {
                    // Añadir los valores de los filtros
                    d.categoria_id = filtroCategoria;
                    d.marca_id = filtroMarca;
                    d.disponibilidad = filtroDisponibilidad;
                    d._timestamp = new Date().getTime();
                    return d;
                },
                // Manejo de errores en la solicitud
                error: function(xhr, error, thrown) {
                    console.error('Error en solicitud AJAX:', error, thrown);
                    console.error('Respuesta del servidor:', xhr.responseText);
                    
                    // Mostrar mensaje de error al usuario
                    let errorMsg = 'Error al cargar los datos de la tabla.';
                    if (xhr.status === 500) errorMsg = 'Error interno del servidor.';
                    if (xhr.status === 404) errorMsg = 'Recurso no encontrado.';
                    if (xhr.status === 403) errorMsg = 'Acceso denegado.';
                    
                    mostrarError(errorMsg + " Por favor, inténtelo de nuevo.");
                }
            },
            // Definición de columnas
            columns: [
                { data: 'imagen', orderable: false },
                { data: 'nombre' },
                { data: 'precio' },
                { data: 'categoria' },
                { data: 'marca' },
                { data: 'stock' },
                { data: 'disponible', orderable: false },
                { data: 'acciones', orderable: false }
            ],
            // Opciones de idioma
            language: {
                url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json',
                // Definir traducciones locales para mensajes comunes por si falla la carga del archivo de idioma
                loadingRecords: 'Cargando...',
                processing: 'Procesando...',
                search: 'Buscar:',
                emptyTable: 'No hay datos disponibles',
                zeroRecords: 'No se encontraron registros coincidentes'
            },
            // Longitud de página
            pageLength: 10,
            // Opciones de longitud
            lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, 'Todos']]
        });
        
        // Inicializar tooltips cada vez que se redibuja la tabla
        productosTable.on('draw', function() {
            setupTooltips();
        });
        
        // Configurar eventos para los filtros
        setupFiltros();
        
        console.log("DataTable inicializado correctamente");
        
    } catch (error) {
        console.error("Error al inicializar DataTable:", error);
        mostrarError("Error al inicializar la tabla. Por favor, recargue la página.");
    }
}

/**
 * Configura eventos para los filtros
 */
function setupFiltros() {
    console.log("Configurando eventos para filtros...");
    
    // Botón para aplicar filtros
    const btnAplicarFiltros = document.getElementById('aplicar-filtros');
    if (btnAplicarFiltros) {
        btnAplicarFiltros.addEventListener('click', function() {
            filtroCategoria = document.getElementById('filtro-categoria').value;
            filtroMarca = document.getElementById('filtro-marca').value;
            filtroDisponibilidad = document.getElementById('filtro-disponibilidad').value;
            
            // Mostrar indicadores de filtros activos
            actualizarIndicadoresFiltros();
            
            // Recargar la tabla con los filtros
            if (productosTable) {
                productosTable.ajax.reload();
            }
        });
    }

    // Botón para limpiar filtros
    const btnLimpiarFiltros = document.getElementById('limpiar-filtros');
    if (btnLimpiarFiltros) {
        btnLimpiarFiltros.addEventListener('click', function() {
            // Resetear valores de los filtros
            document.getElementById('filtro-categoria').value = '';
            document.getElementById('filtro-marca').value = '';
            document.getElementById('filtro-disponibilidad').value = '';
            
            // Limpiar variables
            filtroCategoria = '';
            filtroMarca = '';
            filtroDisponibilidad = '';
            
            // Actualizar indicadores
            actualizarIndicadoresFiltros();
            
            // Recargar la tabla
            if (productosTable) {
                productosTable.ajax.reload();
            }
        });
    }
}

/**
 * Actualiza los indicadores visuales de filtros activos
 */
function actualizarIndicadoresFiltros() {
    const indicadoresDiv = document.getElementById('filtros-activos');
    
    if (!indicadoresDiv) {
        // Crear el contenedor si no existe
        const container = document.querySelector('.d-flex.justify-content-between.align-items-center.mb-4');
        if (container) {
            const nuevoDiv = document.createElement('div');
            nuevoDiv.id = 'filtros-activos';
            nuevoDiv.className = 'filtros-activos mt-2';
            container.parentNode.insertBefore(nuevoDiv, container.nextSibling);
        }
    }
    
    // Obtener el contenedor (ahora seguro que existe)
    const contenedor = document.getElementById('filtros-activos');
    if (!contenedor) return;
    
    contenedor.innerHTML = '';
    
    // Array para almacenar textos de filtros activos
    const filtrosActivos = [];
    
    // Verificar cada filtro
    if (filtroCategoria) {
        const select = document.getElementById('filtro-categoria');
        if (select && select.selectedIndex >= 0) {
            const texto = select.options[select.selectedIndex].text;
            filtrosActivos.push(`<span class="badge bg-info me-2">Categoría: ${texto}</span>`);
        }
    }
    
    if (filtroMarca) {
        const select = document.getElementById('filtro-marca');
        if (select && select.selectedIndex >= 0) {
            const texto = select.options[select.selectedIndex].text;
            filtrosActivos.push(`<span class="badge bg-info me-2">Marca: ${texto}</span>`);
        }
    }
    
    if (filtroDisponibilidad) {
        const select = document.getElementById('filtro-disponibilidad');
        if (select && select.selectedIndex >= 0) {
            const texto = select.options[select.selectedIndex].text;
            filtrosActivos.push(`<span class="badge bg-info me-2">Disponibilidad: ${texto}</span>`);
        }
    }
    
    // Si hay filtros activos, mostrarlos
    if (filtrosActivos.length > 0) {
        contenedor.innerHTML = '<div class="d-flex align-items-center mb-3">' +
                              '<strong class="me-2">Filtros activos:</strong>' +
                              filtrosActivos.join('') +
                              '</div>';
    }
}

/**
 * Configura tooltips para las miniaturas de productos
 */
function setupTooltips() {
    // Verificar si Bootstrap está disponible
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip !== 'undefined') {
        // Intentar disponer los tooltips existentes
        try {
            jQuery('.product-thumbnail[data-bs-toggle="tooltip"]').tooltip('dispose');
        } catch (e) {
            // Ignorar errores
        }
        
        // Inicializar nuevos tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('.product-thumbnail[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                placement: 'right',
                boundary: 'window'
            });
        });
    }
}

/**
 * Limpia la caché de imágenes y recarga la tabla
 * Esta función se expone globalmente para poder llamarla desde botones HTML
 */
window.limpiarCacheImagenes = function() {
    if (!productosTable) {
        console.error("La tabla no está inicializada");
        return;
    }
    
    // Mostrar indicador de carga si toastr está disponible
    if (typeof toastr !== 'undefined') {
        toastr.info('Refrescando imágenes...', '', { timeOut: 2000 });
    } else {
        mostrarInfo('Refrescando imágenes...');
    }
    
    // Recargar la tabla forzando una nueva solicitud
    productosTable.ajax.reload(null, false);
    
    // Notificar al usuario
    setTimeout(function() {
        if (typeof toastr !== 'undefined') {
            toastr.success('Imágenes actualizadas correctamente');
        } else {
            mostrarExito('Imágenes actualizadas correctamente');
        }
    }, 2000);
}

/**
 * Recarga la tabla de productos
 * Esta función se expone globalmente para poder llamarla desde botones HTML
 */
window.recargarTabla = function() {
    console.log("Recargando tabla manualmente...");
    if (productosTable) {
        productosTable.ajax.reload(null, false);
        console.log("Tabla recargada");
    } else {
        console.error("La tabla no está inicializada");
        initDataTable(); // Intentar inicializar si no existe
    }
}

/**
 * Obtiene el valor de una cookie
 * @param {string} name - Nombre de la cookie
 * @returns {string} Valor de la cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Muestra un mensaje de error
 * @param {string} mensaje - Mensaje de error
 */
function mostrarError(mensaje) {
    const tablaContainer = document.querySelector('#productos-table');
    if (tablaContainer) {
        tablaContainer.insertAdjacentHTML('beforebegin', 
            `<div class="alert alert-danger alert-dismissible fade show">${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`);
    }
    
    // También usar toastr si está disponible
    if (typeof toastr !== 'undefined') {
        toastr.error(mensaje);
    }
}

/**
 * Muestra un mensaje informativo
 * @param {string} mensaje - Mensaje informativo
 */
function mostrarInfo(mensaje) {
    const tablaContainer = document.querySelector('#productos-table');
    if (tablaContainer) {
        tablaContainer.insertAdjacentHTML('beforebegin', 
            `<div class="alert alert-info alert-dismissible fade show">${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`);
    }
    
    // También usar toastr si está disponible
    if (typeof toastr !== 'undefined') {
        toastr.info(mensaje);
    }
}

/**
 * Muestra un mensaje de éxito
 * @param {string} mensaje - Mensaje de éxito
 */
function mostrarExito(mensaje) {
    const tablaContainer = document.querySelector('#productos-table');
    if (tablaContainer) {
        tablaContainer.insertAdjacentHTML('beforebegin', 
            `<div class="alert alert-success alert-dismissible fade show">${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`);
    }
    
    // También usar toastr si está disponible
    if (typeof toastr !== 'undefined') {
        toastr.success(mensaje);
    }
}