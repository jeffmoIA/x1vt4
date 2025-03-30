/**
 * imagen_gestion.js - Gestión optimizada de imágenes para productos
 * 
 * Este script maneja:
 * - Adición de nuevas imágenes al formset
 * - Eliminación de bloques de imagen
 * - Gestión de imágenes principales
 * - Reindexación automática de formsets
 * - Validación de envío de formulario
 */

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos principales del DOM
    const imagenesContainer = document.getElementById('imagenes-container');
    const imagenesTotal = document.getElementById('id_imagenes-TOTAL_FORMS');
    const addImagenButton = document.getElementById('add-imagen');
    const form = document.getElementById('producto-form');
    
    // Configuración inicial
    inicializarBotonesEliminar();
    setupPrincipalImageHandlers();
    observarNuevosBloques();
    
    // Configuración de botones de acción
    setupBotonesAccion();
    
    /**
     * Inicializa los botones de eliminar para todos los bloques existentes
     */
    function inicializarBotonesEliminar() {
        console.log('Inicializando botones de eliminar bloques...');
        
        // Eliminar botones existentes para evitar duplicados
        document.querySelectorAll('.btn-eliminar-bloque').forEach(btn => btn.remove());
        
        // Verificar que el contenedor existe
        if (!imagenesContainer) {
            console.error('No se encontró el contenedor de imágenes (#imagenes-container)');
            return;
        }
        
        // Agregar botones a cada bloque
        Array.from(imagenesContainer.children).forEach(function(bloque) {
            agregarBotonEliminar(bloque);
        });
    }
    
    /**
     * Agrega un botón de eliminar a un bloque de imagen
     * @param {HTMLElement} bloque - El bloque de imagen
     */
    function agregarBotonEliminar(bloque) {
        // Verificar si ya tiene un botón
        if (bloque.querySelector('.btn-eliminar-bloque')) {
            return;
        }
        
        // Crear contenedor para el botón (ayuda con el espaciado)
        const contenedorBoton = document.createElement('div');
        contenedorBoton.className = 'text-center mt-3 mb-2 eliminar-container';
        
        // Crear el botón
        const boton = document.createElement('button');
        boton.type = 'button';
        boton.className = 'btn btn-danger btn-eliminar-bloque w-100';
        boton.innerHTML = '<i class="fas fa-trash"></i> Eliminar esta imagen';
        
        // Agregar evento de clic
        boton.addEventListener('click', function() {
            if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                eliminarBloque(bloque, boton);
            }
        });
        
        // Agregar botón al contenedor y el contenedor al bloque
        contenedorBoton.appendChild(boton);
        bloque.appendChild(contenedorBoton);
    }
    
    /**
     * Elimina un bloque de imagen, ya sea marcándolo como eliminado o removiéndolo del DOM
     * @param {HTMLElement} bloque - El bloque a eliminar
     * @param {HTMLElement} boton - El botón que inició la acción
     */
    function eliminarBloque(bloque, boton) {
        // Buscar el checkbox DELETE (existe en items ya guardados en BD)
        const deleteCheckbox = bloque.querySelector('input[id$="-DELETE"]');
        
        if (deleteCheckbox) {
            // Marcar para eliminación (no eliminar del DOM)
            deleteCheckbox.checked = true;
            
            // Aplicar estilo visual para indicar eliminación pendiente
            bloque.classList.add('bloque-eliminando');
            
            // Cambiar el botón a "Restaurar"
            boton.className = 'btn btn-warning btn-eliminar-bloque w-100';
            boton.innerHTML = '<i class="fas fa-undo"></i> Restaurar imagen';
            
            // Cambiar comportamiento del botón para permitir restaurar
            boton.removeEventListener('click', arguments.callee);
            boton.addEventListener('click', function() {
                // Desmarcar el checkbox
                deleteCheckbox.checked = false;
                
                // Restaurar estilos
                bloque.classList.remove('bloque-eliminando');
                
                // Restaurar botón original
                boton.className = 'btn btn-danger btn-eliminar-bloque w-100';
                boton.innerHTML = '<i class="fas fa-trash"></i> Eliminar esta imagen';
                
                // Restaurar comportamiento original
                boton.removeEventListener('click', arguments.callee);
                boton.addEventListener('click', function() {
                    if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                        eliminarBloque(bloque, boton);
                    }
                });
            });
        } else {
            // Para nuevas imágenes, eliminar directamente del DOM
            bloque.remove();
            
            // Actualizar índices
            actualizarIndicesFormularios();
        }
    }
    
    /**
     * Actualiza los índices de todos los formularios para mantener secuencia correcta
     */
    function actualizarIndicesFormularios() {
        if (!imagenesContainer || !imagenesTotal) return;
        
        // Obtener todos los bloques
        const bloques = Array.from(imagenesContainer.children);
        
        // Actualizar contador de formularios
        imagenesTotal.value = bloques.length;
        console.log('TOTAL_FORMS actualizado:', bloques.length);
        
        // Re-indexar todos los campos
        bloques.forEach((bloque, index) => {
            // Actualizar inputs
            bloque.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name) {
                    input.name = input.name.replace(/-\d+-/, `-${index}-`);
                }
                if (input.id) {
                    input.id = input.id.replace(/-\d+-/, `-${index}-`);
                }
            });
            
            // Actualizar labels
            bloque.querySelectorAll('label').forEach(label => {
                if (label.htmlFor) {
                    label.htmlFor = label.htmlFor.replace(/-\d+-/, `-${index}-`);
                }
            });
        });
    }
    
    /**
     * Configura el manejo de eventos para imágenes principales
     */
    function setupPrincipalImageHandlers() {
        const principalCheckboxes = document.querySelectorAll('.principal-checkbox');
        
        principalCheckboxes.forEach(checkbox => {
            // Eliminar handlers existentes
            checkbox.removeEventListener('change', handlePrincipalCheckboxChange);
            // Agregar nuevo handler
            checkbox.addEventListener('change', handlePrincipalCheckboxChange);
        });
    }
    
    /**
     * Maneja los cambios en los checkboxes de imagen principal
     */
    function handlePrincipalCheckboxChange() {
        if (this.checked) {
            // Desmarcar todos los demás checkboxes
            document.querySelectorAll('.principal-checkbox').forEach(cb => {
                if (cb !== this) cb.checked = false;
            });
            
            // Quitar resaltado de todas las tarjetas
            document.querySelectorAll('.imagen-form .card').forEach(card => {
                card.classList.remove('border-primary');
            });
            
            // Resaltar esta tarjeta
            const currentForm = this.closest('.imagen-form');
            if (currentForm) {
                const card = currentForm.querySelector('.card');
                if (card) {
                    card.classList.add('border-primary');
                }
            }
        }
    }
    
    /**
     * Configura el manejo del botón de agregar imagen
     */
    if (addImagenButton && imagenesContainer) {
        addImagenButton.addEventListener('click', function() {
            const forms = document.getElementsByClassName('imagen-form');
            
            if (forms.length === 0) {
                console.error("No hay formularios de imagen para clonar");
                return;
            }
            
            // Obtener el índice del nuevo formulario
            const formCount = parseInt(imagenesTotal.value || '0');
            console.log(`Añadiendo imagen #${formCount}`);
            
            // Clonar el primer formulario
            const firstForm = forms[0];
            const newForm = firstForm.cloneNode(true);
            
            // Actualizar IDs y nombres
            updateFormAttributes(newForm, 'imagenes', formCount);
            
            // Limpiar valores
            newForm.querySelectorAll('input[type="text"], input[type="number"], input[type="file"]')
                .forEach(input => {
                    input.value = '';
                });
            
            newForm.querySelectorAll('input[type="checkbox"]')
                .forEach(checkbox => {
                    checkbox.checked = false;
                });
            
            // Eliminar vista previa de imagen si existe
            const imgPreview = newForm.querySelector('.image-container');
            if (imgPreview) {
                imgPreview.remove();
            }
            
            // Quitar borde de imagen principal
            const card = newForm.querySelector('.card');
            if (card) {
                card.classList.remove('border-primary');
            }
            
            // Añadir al DOM
            imagenesContainer.appendChild(newForm);
            
            // Actualizar contador
            imagenesTotal.value = (formCount + 1).toString();
            
            // Agregar botón eliminar al nuevo bloque
            agregarBotonEliminar(newForm);
            
            // Actualizar handlers para checkbox principal
            setupPrincipalImageHandlers();
        });
    }
    
    /**
     * Actualiza atributos de formulario al clonar
     */
    function updateFormAttributes(element, prefix, index) {
        // Actualizar IDs
        element.querySelectorAll(`[id^="id_${prefix}-"]`).forEach(el => {
            const oldId = el.id;
            const newId = oldId.replace(new RegExp(`${prefix}-\\d+`), `${prefix}-${index}`);
            el.id = newId;
        });
        
        // Actualizar names
        element.querySelectorAll(`[name^="${prefix}-"]`).forEach(el => {
            const oldName = el.name;
            const newName = oldName.replace(new RegExp(`${prefix}-\\d+`), `${prefix}-${index}`);
            el.name = newName;
        });
        
        // Actualizar labels
        element.querySelectorAll(`label[for^="id_${prefix}-"]`).forEach(label => {
            if (label.htmlFor) {
                const oldFor = label.htmlFor;
                const newFor = oldFor.replace(new RegExp(`${prefix}-\\d+`), `${prefix}-${index}`);
                label.htmlFor = newFor;
            }
        });
    }
    
    /**
     * Observa la adición de nuevos bloques para agregarles botones
     */
    function observarNuevosBloques() {
        // Usar MutationObserver para detectar cambios en el contenedor
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Procesar nuevos nodos
                    mutation.addedNodes.forEach(function(nodo) {
                        if (nodo.nodeType === 1 && nodo.classList.contains('imagen-form')) {
                            // Es un elemento y es un formulario de imagen
                            agregarBotonEliminar(nodo);
                        }
                    });
                }
            });
        });
        
        // Configurar observador
        observer.observe(imagenesContainer, {
            childList: true
        });
    }
    
    /**
     * Configura los botones de acción principal del formulario
     */
    function setupBotonesAccion() {
        const btnAplicarCambios = document.getElementById('btn-aplicar-cambios');
        const btnGuardarSalir = document.getElementById('btn-guardar-salir');
        
        // Botón de aplicar cambios (AJAX)
        if (btnAplicarCambios) {
            btnAplicarCambios.addEventListener('click', function(event) {
                event.preventDefault();
                
                // Actualizar índices de formularios antes de enviar
                actualizarIndicesFormularios();
                
                // Preparar datos
                const formData = new FormData(form);
                formData.append('aplicar_cambios', 'true');
                
                // Mostrar indicador de carga
                btnAplicarCambios.disabled = true;
                btnAplicarCambios.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Aplicando...';
                
                // Enviar solicitud AJAX usando Fetch API
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
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
                    // Restaurar botón
                    btnAplicarCambios.disabled = false;
                    btnAplicarCambios.innerHTML = '<i class="fas fa-check-circle"></i> Aplicar cambios';
                    
                    if (data.success) {
                        // Éxito - mostrar notificación
                        mostrarNotificacion('success', data.message || 'Cambios aplicados exitosamente');
                        
                        // Actualizar URL si es producto nuevo
                        if (data.producto_id) {
                            const currentPath = window.location.pathname;
                            if (currentPath.includes('/crear/')) {
                                history.replaceState(
                                    null, 
                                    '', 
                                    currentPath.replace('/crear/', `/${data.producto_id}/editar/`)
                                );
                            }
                        }
                    } else {
                        // Error - mostrar notificación
                        mostrarNotificacion('error', data.error || 'Error al aplicar cambios');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    
                    // Restaurar botón
                    btnAplicarCambios.disabled = false;
                    btnAplicarCambios.innerHTML = '<i class="fas fa-check-circle"></i> Aplicar cambios';
                    
                    // Mostrar error
                    mostrarNotificacion('error', 'Error de conexión: ' + error.message);
                });
            });
        }
        
        // Botón de guardar y salir (submit normal)
        if (btnGuardarSalir) {
            btnGuardarSalir.addEventListener('click', function(event) {
                event.preventDefault();
                
                // Actualizar índices antes de enviar
                actualizarIndicesFormularios();
                
                // Añadir campo para indicar redirección
                const inputRedirigir = document.createElement('input');
                inputRedirigir.type = 'hidden';
                inputRedirigir.name = 'redirigir';
                inputRedirigir.value = 'true';
                form.appendChild(inputRedirigir);
                
                // Deshabilitar botón y mostrar carga
                btnGuardarSalir.disabled = true;
                btnGuardarSalir.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Guardando...';
                
                // Enviar formulario
                form.submit();
            });
        }
    }
    
    /**
     * Muestra notificaciones usando toastr o alertas Bootstrap
     * @param {string} tipo - Tipo de notificación: success, error, warning, info
     * @param {string} mensaje - Texto a mostrar
     */
    function mostrarNotificacion(tipo, mensaje) {
        // Si toastr está disponible, usarlo
        if (typeof toastr !== 'undefined') {
            toastr[tipo](mensaje);
            return;
        }
        
        // Si no, usar alertas Bootstrap
        let alertClass = 'alert-info';
        if (tipo === 'success') alertClass = 'alert-success';
        if (tipo === 'error') alertClass = 'alert-danger';
        if (tipo === 'warning') alertClass = 'alert-warning';
        
        // Crear alerta
        const alertHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Insertar al inicio del formulario
        const cardBody = form.closest('.card-body');
        if (cardBody) {
            // Eliminar alertas anteriores
            cardBody.querySelectorAll('.alert').forEach(alert => alert.remove());
            
            // Agregar nueva alerta
            cardBody.insertAdjacentHTML('afterbegin', alertHTML);
            
            // Auto-cerrar después de 5 segundos
            setTimeout(() => {
                const alerts = cardBody.querySelectorAll('.alert');
                alerts.forEach(alert => {
                    if (typeof bootstrap !== 'undefined') {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    } else {
                        alert.remove();
                    }
                });
            }, 5000);
        }
    }
    
    /**
     * Validar formulario antes de enviar
     */
    if (form) {
        form.addEventListener('submit', function(event) {
            // Actualizar índices de formularios
            actualizarIndicesFormularios();
        });
    }
});