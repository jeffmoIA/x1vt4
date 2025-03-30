/**
 * Controlador dedicado para los botones de acción del formulario de producto
 * - Maneja "Aplicar cambios" con AJAX
 * - Maneja "Guardar y salir" con submit normal
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando controlador de botones de acción...');
    
    // Referencias a elementos principales
    const form = document.getElementById('producto-form');
    const btnAplicar = document.getElementById('btn-aplicar-cambios');
    const btnGuardar = document.getElementById('btn-guardar-salir');
    
    // Verificar elementos
    if (!form) {
        console.error('Error: No se encontró el formulario de producto (#producto-form)');
        return;
    }
    
    // Verificar si hay botones de acción en el formulario
    if (!btnAplicar && !btnGuardar) {
        console.error('Error: No se encontraron los botones de acción');
        
        // Buscar botones por texto
        form.querySelectorAll('button').forEach(btn => {
            const text = btn.textContent.toLowerCase();
            if (text.includes('aplicar') || text.includes('cambios')) {
                console.log('Botón aplicar encontrado por texto:', btn);
                configurarBotonAplicar(btn);
            } else if (text.includes('guardar') || text.includes('salir')) {
                console.log('Botón guardar encontrado por texto:', btn);
                configurarBotonGuardar(btn);
            }
        });
    } else {
        // Configurar los botones encontrados por ID
        if (btnAplicar) configurarBotonAplicar(btnAplicar);
        if (btnGuardar) configurarBotonGuardar(btnGuardar);
    }
    
    /**
     * Configura el botón "Aplicar cambios" con AJAX
     */
    function configurarBotonAplicar(boton) {
        console.log('Configurando botón Aplicar cambios');
        
        // Eliminar todos los event listeners existentes
        const nuevoBtn = boton.cloneNode(true);
        boton.parentNode.replaceChild(nuevoBtn, boton);
        
        // Añadir nuevo evento
        nuevoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Click en botón Aplicar cambios');
            
            // Verificar necesidad de reindexar formsets
            actualizarFormsets();
            
            // Prepare FormData
            const formData = new FormData(form);
            formData.append('aplicar_cambios', 'true');
            
            // Mostrar estado de carga
            this.disabled = true;
            const textoOriginal = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Aplicando...';
            
            // Enviar solicitud AJAX
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
                this.disabled = false;
                this.innerHTML = textoOriginal;
                
                if (data.success) {
                    // Mostrar mensaje de éxito
                    mostrarNotificacion('success', data.message || 'Cambios aplicados correctamente');
                    
                    // Actualizar URL si necesario (producto nuevo)
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
                    // Mostrar error
                    mostrarNotificacion('error', data.error || 'Error al aplicar cambios');
                }
            })
            .catch(error => {
                console.error('Error en solicitud:', error);
                
                // Restaurar botón
                this.disabled = false;
                this.innerHTML = textoOriginal;
                
                // Mostrar error
                mostrarNotificacion('error', 'Error de conexión: ' + error.message);
            });
        });
    }
    
    /**
     * Configura el botón "Guardar y salir" para envío normal
     */
    function configurarBotonGuardar(boton) {
        console.log('Configurando botón Guardar y salir');
        
        // Eliminar todos los event listeners existentes
        const nuevoBtn = boton.cloneNode(true);
        boton.parentNode.replaceChild(nuevoBtn, boton);
        
        // Añadir nuevo evento
        nuevoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Click en botón Guardar y salir');
            
            // Verificar necesidad de reindexar formsets
            actualizarFormsets();
            
            // Añadir campo para redirección
            let redirectInput = form.querySelector('input[name="redirigir"]');
            if (!redirectInput) {
                redirectInput = document.createElement('input');
                redirectInput.type = 'hidden';
                redirectInput.name = 'redirigir';
                form.appendChild(redirectInput);
            }
            redirectInput.value = 'true';
            
            // Mostrar estado de carga
            this.disabled = true;
            const textoOriginal = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
            
            // Pequeño retraso para que el spinner se muestre
            setTimeout(() => {
                // Enviar formulario
                form.submit();
            }, 100);
        });
    }
    
    /**
     * Actualiza los índices de los formsets antes de enviar
     */
    function actualizarFormsets() {
        // Buscar todos los contenedores de formsets
        document.querySelectorAll('[id$="-container"]').forEach(container => {
            // Identificar prefijo por el ID del contenedor
            const idMatch = container.id.match(/(.+)-container$/);
            if (!idMatch) return;
            
            const prefix = idMatch[1];
            const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
            
            if (!totalFormsInput) return;
            
            // Contar elementos reales
            const elements = container.querySelectorAll(`.${prefix}-form, [class*="${prefix}"]`);
            
            // Actualizar contador
            totalFormsInput.value = elements.length.toString();
            console.log(`Formset ${prefix}: actualizado a ${elements.length} elementos`);
            
            // Reindexar elementos
            elements.forEach((el, index) => {
                el.querySelectorAll('input, select, textarea').forEach(input => {
                    if (input.name && input.name.match(new RegExp(`^${prefix}-\\d+`))) {
                        input.name = input.name.replace(
                            new RegExp(`^${prefix}-\\d+`), 
                            `${prefix}-${index}`
                        );
                    }
                });
            });
        });
    }
    
    /**
     * Muestra notificaciones al usuario
     */
    function mostrarNotificacion(tipo, mensaje) {
        // Probar primero con toastr
        if (typeof toastr !== 'undefined') {
            toastr[tipo](mensaje);
            return;
        }
        
        // Luego con SweetAlert2
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: tipo === 'error' ? 'error' : 'success',
                title: tipo === 'error' ? 'Error' : 'Éxito',
                text: mensaje,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
            return;
        }
        
        // Finalmente, usar alertas nativas de Bootstrap
        let containerDiv = document.getElementById('notifications-container');
        if (!containerDiv) {
            containerDiv = document.createElement('div');
            containerDiv.id = 'notifications-container';
            containerDiv.style.position = 'fixed';
            containerDiv.style.top = '20px';
            containerDiv.style.right = '20px';
            containerDiv.style.zIndex = '9999';
            document.body.appendChild(containerDiv);
        }
        
        // Crear alerta
        const alert = document.createElement('div');
        alert.className = `alert alert-${tipo === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alert.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Añadir al contenedor
        containerDiv.appendChild(alert);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    }
});