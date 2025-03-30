/**
 * Gestor del formulario de productos
 * 
 * Una solución completa y optimizada para:
 * - Gestión de imágenes
 * - Botones de acción
 * - Manejo de formsets
 * 
 * Sin interferir con otras funcionalidades
 */
const ProductFormManager = (function() {
    // Referencias a elementos del DOM
    let form;
    let imageContainer;
    let totalFormsInput;
    let btnAplicar;
    let btnGuardar;
    let btnAnadir;
    let formPrefix = 'imagenes';
    
    // Estado interno
    let isProcessing = false;
    
    /**
     * Inicializa el gestor
     */
    function init() {
        console.log('Inicializando gestor de formulario de producto...');
        
        // Obtener referencias principales
        form = document.querySelector('form#producto-form') || document.querySelector('form');
        imageContainer = document.getElementById('imagenes-container');
        totalFormsInput = document.querySelector('input[name="imagenes-TOTAL_FORMS"]');
        
        // Botones principales
        btnAplicar = document.querySelector('[id="btn-aplicar-cambios"], button:contains("Aplicar")');
        btnGuardar = document.querySelector('[id="btn-guardar-salir"], button:contains("Guardar")');
        btnAnadir = document.querySelector('[id="add-imagen"], button:contains("Añadir")');
        
        // Si no podemos encontrar por ID o contains, usar querySelectorAll
        if (!btnAplicar || !btnGuardar) {
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.toLowerCase();
                if (text.includes('aplicar') || text.includes('cambios')) {
                    btnAplicar = btn;
                } else if (text.includes('guardar') || text.includes('salir')) {
                    btnGuardar = btn;
                } else if (text.includes('añadir') || text.includes('agregar')) {
                    btnAnadir = btn;
                }
            });
        }
        
        // Verificar elementos necesarios
        if (!form) {
            console.error('No se pudo encontrar el formulario principal');
            return false;
        }
        
        if (!imageContainer) {
            console.warn('No se pudo encontrar el contenedor de imágenes, algunas funciones estarán limitadas');
        }
        
        if (!totalFormsInput) {
            console.warn('No se pudo encontrar el campo TOTAL_FORMS, la gestión de formsets estará limitada');
        }
        
        // Configuración inicial
        setupActionButtons();
        setupImageManagement();
        
        console.log('Gestor de formulario inicializado con éxito');
        return true;
    }
    
    /**
     * Configura los botones de acción principales
     */
    function setupActionButtons() {
        // Limpiar y configurar botón Aplicar
        if (btnAplicar) {
            console.log('Configurando botón Aplicar cambios:', btnAplicar);
            const newBtnAplicar = btnAplicar.cloneNode(true);
            btnAplicar.parentNode.replaceChild(newBtnAplicar, btnAplicar);
            btnAplicar = newBtnAplicar;
            
            btnAplicar.addEventListener('click', handleAplicarClick);
        } else {
            console.error('No se pudo encontrar el botón Aplicar cambios');
        }
        
        // Limpiar y configurar botón Guardar
        if (btnGuardar) {
            console.log('Configurando botón Guardar y salir:', btnGuardar);
            const newBtnGuardar = btnGuardar.cloneNode(true);
            btnGuardar.parentNode.replaceChild(newBtnGuardar, btnGuardar);
            btnGuardar = newBtnGuardar;
            
            btnGuardar.addEventListener('click', handleGuardarClick);
        } else {
            console.error('No se pudo encontrar el botón Guardar y salir');
        }
    }
    
    /**
     * Configura la gestión de imágenes
     */
    function setupImageManagement() {
        if (!imageContainer || !totalFormsInput) return;
        
        // Mejorar apariencia
        improveImageBlocks();
        
        // Configurar botones de eliminación existentes
        setupDeleteButtons();
        
        // Configurar botón añadir
        if (btnAnadir) {
            console.log('Configurando botón Añadir imagen:', btnAnadir);
            const newBtnAnadir = btnAnadir.cloneNode(true);
            btnAnadir.parentNode.replaceChild(newBtnAnadir, btnAnadir);
            btnAnadir = newBtnAnadir;
            
            btnAnadir.addEventListener('click', handleAnadirClick);
        } else {
            console.warn('No se pudo encontrar el botón Añadir imagen');
        }
    }
    
    /**
     * Mejora la apariencia de los bloques de imagen
     */
    function improveImageBlocks() {
        // Aplicar flex layout al contenedor
        if (imageContainer) {
            Object.assign(imageContainer.style, {
                display: 'flex',
                flexWrap: 'wrap',
                gap: '15px',
                margin: '10px 0'
            });
        }
        
        // Mejorar cada bloque
        document.querySelectorAll('.imagen-form, [id^="imagenes-"]').forEach(block => {
            if (!block.classList.contains('imagen-form')) {
                block.classList.add('imagen-form');
            }
            
            // Aplicar estilos básicos
            Object.assign(block.style, {
                border: '1px solid #dee2e6',
                padding: '15px',
                borderRadius: '5px',
                backgroundColor: '#fff',
                flex: '0 0 300px',
                position: 'relative'
            });
            
            // Mejorar imagen si existe
            const img = block.querySelector('img');
            if (img) {
                Object.assign(img.style, {
                    maxWidth: '100%',
                    maxHeight: '150px',
                    display: 'block',
                    margin: '0 auto 10px'
                });
            }
        });
    }
    
    /**
     * Configura los botones de eliminación
     */
    function setupDeleteButtons() {
        document.querySelectorAll('button, .btn-eliminar-imagen, [class*="eliminar"]').forEach(btn => {
            if (btn.textContent.includes('Eliminar') || 
                btn.textContent.includes('eliminar')) {
                
                const newBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(newBtn, btn);
                
                newBtn.addEventListener('click', handleEliminarClick);
            }
        });
    }
    
    /**
     * Manejador para el botón Aplicar cambios
     */
    function handleAplicarClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (isProcessing) return;
        isProcessing = true;
        
        console.log('Procesando Aplicar cambios...');
        
        // Preparar formulario
        updateFormsets();
        
        // Indicador de carga
        const originalText = this.innerHTML;
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Aplicando...';
        
        // Preparar datos
        const formData = new FormData(form);
        formData.append('aplicar_cambios', 'true');
        
        // Enviar solicitud
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
            
            // Verificar tipo de contenido
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                return { success: true, message: 'Cambios aplicados correctamente' };
            }
        })
        .then(data => {
            console.log('Respuesta del servidor:', data);
            
            // Restaurar botón
            this.disabled = false;
            this.innerHTML = originalText;
            
            // Mostrar mensaje
            showNotification(
                data.success ? 'success' : 'error',
                data.success ? (data.message || 'Cambios aplicados correctamente') : (data.error || 'Error al aplicar cambios')
            );
            
            // Para solucionar el problema de los cambios no aplicados,
            // podemos recargar la página automáticamente
            if (data.success) {
                // Actualizar URL si es un producto nuevo
                if (data.producto_id) {
                    const currentPath = window.location.pathname;
                    if (currentPath.includes('/crear/')) {
                        const newPath = currentPath.replace('/crear/', `/${data.producto_id}/editar/`);
                        window.location.href = newPath;
                        return;
                    }
                }
                
                // Pequeña espera antes de recargar para que se vea el mensaje
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
            
            isProcessing = false;
        })
        .catch(error => {
            console.error('Error en solicitud:', error);
            
            // Restaurar botón
            this.disabled = false;
            this.innerHTML = originalText;
            
            // Mostrar error
            showNotification('error', 'Error: ' + error.message);
            
            isProcessing = false;
        });
    }
    
    /**
     * Manejador para el botón Guardar y salir
     */
    function handleGuardarClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (isProcessing) return;
        isProcessing = true;
        
        console.log('Procesando Guardar y salir...');
        
        // Preparar formulario
        updateFormsets();
        
        // Añadir campo para redirección
        let redirectInput = form.querySelector('input[name="redirigir"]');
        if (!redirectInput) {
            redirectInput = document.createElement('input');
            redirectInput.type = 'hidden';
            redirectInput.name = 'redirigir';
            form.appendChild(redirectInput);
        }
        redirectInput.value = 'true';
        
        // Indicador de carga
        const originalText = this.innerHTML;
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
        
        // Enviar formulario después de un breve retraso para que se vea el spinner
        setTimeout(() => {
            form.submit();
        }, 100);
    }
    
    /**
     * Manejador para el botón Añadir imagen
     */
    function handleAnadirClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (isProcessing) return;
        isProcessing = true;
        
        console.log('Añadiendo nueva imagen...');
        
        try {
            // Obtener índice para el nuevo formulario
            const formCount = parseInt(totalFormsInput.value) || 0;
            const newIndex = formCount;
            
            // Crear nuevo bloque
            const newBlock = document.createElement('div');
            newBlock.className = 'imagen-form';
            
            // Aplicar estilos
            Object.assign(newBlock.style, {
                border: '1px solid #dee2e6',
                padding: '15px',
                borderRadius: '5px',
                backgroundColor: '#fff',
                flex: '0 0 300px',
                position: 'relative'
            });
            
            // HTML del bloque
            newBlock.innerHTML = `
                <label>Imagen</label>
                <input type="file" name="${formPrefix}-${newIndex}-imagen" 
                       id="id_${formPrefix}-${newIndex}-imagen" 
                       class="form-control mb-3" accept="image/*">
                
                <label>Orden</label>
                <input type="number" name="${formPrefix}-${newIndex}-orden" 
                       id="id_${formPrefix}-${newIndex}-orden" 
                       class="form-control mb-3" value="${newIndex}">
                
                <div class="form-check mb-3">
                    <input type="checkbox" name="${formPrefix}-${newIndex}-es_principal" 
                           id="id_${formPrefix}-${newIndex}-es_principal" 
                           class="form-check-input">
                    <label for="id_${formPrefix}-${newIndex}-es_principal" class="form-check-label">
                        Es imagen principal
                    </label>
                </div>
                
                <label>Título (opcional)</label>
                <input type="text" name="${formPrefix}-${newIndex}-titulo" 
                       id="id_${formPrefix}-${newIndex}-titulo" 
                       class="form-control mb-3">
                
                <button type="button" class="btn btn-danger w-100">
                    Eliminar imagen
                </button>
            `;
            
            // Añadir al contenedor
            imageContainer.appendChild(newBlock);
            
            // Actualizar contador
            totalFormsInput.value = (formCount + 1).toString();
            
            // Configurar botón eliminar
            const deleteBtn = newBlock.querySelector('button');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', handleEliminarClick);
            }
            
            console.log('Nueva imagen añadida con éxito');
        } catch (error) {
            console.error('Error al añadir imagen:', error);
            showNotification('error', 'Error al añadir imagen: ' + error.message);
        }
        
        isProcessing = false;
    }
    
    /**
     * Manejador para botones de eliminar imagen
     */
    function handleEliminarClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (isProcessing) return;
        
        const block = this.closest('.imagen-form') || this.closest('[id^="imagenes-"]');
        if (!block) {
            console.error('No se pudo encontrar el bloque de imagen a eliminar');
            return;
        }
        
        if (confirm('¿Estás seguro de eliminar esta imagen?')) {
            isProcessing = true;
            
            // Buscar checkbox DELETE para imágenes existentes
            const deleteCheckbox = block.querySelector('input[name$="-DELETE"]');
            
            if (deleteCheckbox) {
                // Para imágenes existentes, marcar para eliminar
                deleteCheckbox.checked = true;
                
                // Aplicar estilo "eliminado"
                Object.assign(block.style, {
                    opacity: '0.6',
                    backgroundColor: '#fff0f0',
                    borderColor: '#dc3545',
                    borderStyle: 'dashed'
                });
                
                // Cambiar botón a "Restaurar"
                this.textContent = 'Restaurar';
                this.className = 'btn btn-warning w-100';
                
                // Cambiar comportamiento para restaurar
                const originalBtn = this;
                this.removeEventListener('click', handleEliminarClick);
                this.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Desmarcar checkbox
                    deleteCheckbox.checked = false;
                    
                    // Restaurar apariencia
                    Object.assign(block.style, {
                        opacity: '1',
                        backgroundColor: '#fff',
                        borderColor: '#dee2e6',
                        borderStyle: 'solid'
                    });
                    
                    // Restaurar botón
                    this.textContent = 'Eliminar imagen';
                    this.className = 'btn btn-danger w-100';
                    
                    // Restaurar comportamiento original
                    this.removeEventListener('click', arguments.callee);
                    this.addEventListener('click', handleEliminarClick);
                });
            } else {
                // Para imágenes nuevas, eliminar del DOM
                block.remove();
                
                // Actualizar contador
                if (totalFormsInput) {
                    const currentCount = parseInt(totalFormsInput.value);
                    totalFormsInput.value = (currentCount - 1).toString();
                }
                
                // Reindexar formularios
                updateFormsets();
            }
            
            isProcessing = false;
        }
    }
    
    /**
     * Actualiza los formsets antes de enviar
     */
    function updateFormsets() {
        if (!imageContainer || !totalFormsInput) return;
        
        // Obtener todos los bloques
        const blocks = imageContainer.querySelectorAll('.imagen-form, [id^="imagenes-"]');
        
        // Actualizar contador
        totalFormsInput.value = blocks.length.toString();
        console.log(`Actualizado TOTAL_FORMS a ${blocks.length}`);
        
        // Reindexar cada bloque
        blocks.forEach((block, index) => {
            block.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name && input.name.match(new RegExp(`^${formPrefix}-\\d+`))) {
                    // Mantener la parte después del índice
                    const match = input.name.match(new RegExp(`^${formPrefix}-\\d+-(.*)`));
                    if (match) {
                        const fieldName = match[1];
                        const newName = `${formPrefix}-${index}-${fieldName}`;
                        
                        // Actualizar nombre e ID
                        input.name = newName;
                        if (input.id && input.id.match(new RegExp(`^id_${formPrefix}-\\d+`))) {
                            input.id = `id_${newName}`;
                        }
                    }
                }
            });
            
            // Actualizar labels
            block.querySelectorAll('label[for]').forEach(label => {
                if (label.htmlFor && label.htmlFor.match(new RegExp(`^id_${formPrefix}-\\d+`))) {
                    const match = label.htmlFor.match(new RegExp(`^id_${formPrefix}-\\d+-(.*)`));
                    if (match) {
                        const fieldName = match[1];
                        label.htmlFor = `id_${formPrefix}-${index}-${fieldName}`;
                    }
                }
            });
        });
    }
    
    /**
     * Muestra una notificación al usuario
     */
    function showNotification(type, message) {
        console.log(`Notificación (${type}): ${message}`);
        
        // Intentar usar toastr si está disponible
        if (typeof toastr !== 'undefined') {
            toastr[type](message);
            return;
        }
        
        // Alertas nativas de Bootstrap
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            container.style.minWidth = '250px';
            document.body.appendChild(container);
        }
        
        // Crear alerta
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alert.style.marginBottom = '10px';
        alert.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Añadir al contenedor
        container.appendChild(alert);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    }
    
    // Inicializar y retornar API pública
    return {
        init: init,
        updateFormsets: updateFormsets
    };
})();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', ProductFormManager.init);