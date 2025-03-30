/**
 * Solución definitiva para problemas de gestión de imágenes
 * - Evita duplicación de bloques
 * - Maneja correctamente la eliminación
 * - Corrige problemas de espaciado y visualización
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando solución final para imágenes...');
    
    // Referencias DOM principales
    const contenedor = document.getElementById('imagenes-container');
    const management = document.querySelectorAll('[id$="TOTAL_FORMS"], [id$="INITIAL_FORMS"], [id$="MIN_NUM_FORMS"], [id$="MAX_NUM_FORMS"]');
    
    // Variables de control
    let isProcessing = false;
    let prefix = 'imagenes';
    let totalFormsInput;
    
    // Inicialización
    function init() {
        // Identificar prefijo y contador
        for (let input of management) {
            if (input.id.endsWith('TOTAL_FORMS')) {
                totalFormsInput = input;
                prefix = input.id.replace(/-TOTAL_FORMS$/, '');
                prefix = prefix.replace(/^id_/, '');
                break;
            }
        }
        
        if (!totalFormsInput) {
            console.error('Error crítico: No se pudo encontrar el campo TOTAL_FORMS');
            return false;
        }
        
        console.log(`Formulario identificado: prefijo="${prefix}", total=${totalFormsInput.value}`);
        
        // Aplicar mejoras visuales
        mejorarApariencia();
        
        // Configurar botones existentes
        configurarBotones();
        
        // Eliminar event listeners duplicados
        limpiarEventos();
        
        return true;
    }
    
    // Solo continuar si la inicialización fue exitosa
    if (!init()) return;
    
    /**
     * Mejora la apariencia de los elementos de imagen
     */
    function mejorarApariencia() {
        // Aplicar estilos directamente al contenedor
        Object.assign(contenedor.style, {
            display: 'flex',
            flexWrap: 'wrap',
            gap: '20px',
            margin: '0 -10px'
        });
        
        // Mejorar cada bloque
        Array.from(contenedor.children).forEach(function(bloque) {
            if (!bloque.classList.contains('imagen-form') && 
                !bloque.classList.contains('imagen-bloque')) {
                bloque.classList.add('imagen-form');
            }
            
            Object.assign(bloque.style, {
                flex: '0 1 300px',
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#fff',
                boxShadow: '0 2px 5px rgba(0,0,0,0.08)',
                margin: '5px'
            });
            
            // Mejorar inputs
            bloque.querySelectorAll('input:not([type="checkbox"]), textarea, select').forEach(input => {
                if (!input.classList.contains('form-control')) {
                    input.classList.add('form-control');
                }
                input.style.marginBottom = '10px';
            });
            
            // Mejorar imágenes
            const img = bloque.querySelector('img');
            if (img) {
                Object.assign(img.style, {
                    maxWidth: '100%',
                    height: 'auto',
                    maxHeight: '150px',
                    display: 'block',
                    margin: '0 auto 15px'
                });
            }
            
            // Estilizar botones de eliminar
            const btnEliminar = bloque.querySelector('[class*="eliminar"], [class*="Eliminar"], button');
            if (btnEliminar && 
                (btnEliminar.textContent.includes('Eliminar') || 
                 btnEliminar.textContent.includes('eliminar'))) {
                
                Object.assign(btnEliminar.style, {
                    width: '100%',
                    marginTop: '10px'
                });
                
                btnEliminar.classList.add('btn', 'btn-danger');
            }
        });
    }
    
    /**
     * Configura botones de añadir y eliminar
     */
    function configurarBotones() {
        // Identificar botón de añadir
        const btnAnadir = document.querySelector('button[id="add-imagen"], [class*="anadir"], [class*="añadir"], [class*="agregar"]');
        
        if (!btnAnadir) {
            console.error('No se encontró el botón para añadir imágenes');
            return;
        }
        
        // Limpiar listeners previos
        const nuevoBtn = btnAnadir.cloneNode(true);
        btnAnadir.parentNode.replaceChild(nuevoBtn, btnAnadir);
        
        // Configurar nuevo evento
        nuevoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Evitar múltiples clics
            if (isProcessing) return;
            isProcessing = true;
            
            console.log('Añadiendo nueva imagen...');
            anadirNuevaImagen();
            
            // Habilitar después de un tiempo
            setTimeout(() => {
                isProcessing = false;
            }, 500);
        });
        
        // Configurar botones de eliminar
        const botonesEliminar = document.querySelectorAll('button[class*="eliminar"], [class*="Eliminar"]');
        botonesEliminar.forEach(btn => {
            // Solo procesar si contiene texto de eliminar
            if (!btn.textContent.includes('liminar')) return;
            
            // Eliminar listeners previos
            const nuevoEliminar = btn.cloneNode(true);
            btn.parentNode.replaceChild(nuevoEliminar, btn);
            
            // Añadir nuevo evento
            nuevoEliminar.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                manejarEliminacionImagen(this);
            });
        });
    }
    
    /**
     * Elimina event listeners duplicados
     */
    function limpiarEventos() {
        // Limpiar listeners de eventos añadidos por otros scripts
        document.querySelectorAll('#imagenes-container button').forEach(btn => {
            const nuevo = btn.cloneNode(true);
            btn.parentNode.replaceChild(nuevo, btn);
            
            if (nuevo.textContent.includes('liminar')) {
                nuevo.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    manejarEliminacionImagen(this);
                });
            }
        });
    }
    
    /**
     * Añade una nueva imagen al formulario
     */
    function anadirNuevaImagen() {
        try {
            // Obtener número actual de formularios
            const totalForms = parseInt(totalFormsInput.value);
            const newIndex = totalForms;
            
            console.log(`Añadiendo imagen con índice ${newIndex}`);
            
            // Crear nuevo bloque de imagen
            const nuevoBloque = document.createElement('div');
            nuevoBloque.className = 'imagen-form';
            nuevoBloque.id = `${prefix}-${newIndex}`;
            
            // Estilos para el bloque
            Object.assign(nuevoBloque.style, {
                flex: '0 1 300px',
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#fff',
                boxShadow: '0 2px 5px rgba(0,0,0,0.08)',
                margin: '5px'
            });
            
            // HTML del bloque
            nuevoBloque.innerHTML = `
                <div>
                    <label class="form-label">Imagen</label>
                    <input type="file" name="${prefix}-${newIndex}-imagen" 
                           id="id_${prefix}-${newIndex}-imagen" 
                           class="form-control" accept="image/*">
                </div>
                
                <div style="margin-top:10px;">
                    <label class="form-label">Orden</label>
                    <input type="number" name="${prefix}-${newIndex}-orden" 
                           id="id_${prefix}-${newIndex}-orden" 
                           value="${newIndex}" class="form-control">
                </div>
                
                <div style="margin-top:10px;" class="form-check">
                    <input type="checkbox" name="${prefix}-${newIndex}-es_principal" 
                           id="id_${prefix}-${newIndex}-es_principal"
                           class="form-check-input">
                    <label for="id_${prefix}-${newIndex}-es_principal" class="form-check-label">
                        Es imagen principal
                    </label>
                </div>
                
                <div style="margin-top:10px;">
                    <label class="form-label">Título (opcional)</label>
                    <input type="text" name="${prefix}-${newIndex}-titulo" 
                           id="id_${prefix}-${newIndex}-titulo" 
                           class="form-control">
                </div>
                
                <button type="button" class="btn btn-danger" style="width:100%; margin-top:15px;">
                    Eliminar imagen
                </button>
            `;
            
            // Añadir al contenedor
            contenedor.appendChild(nuevoBloque);
            
            // Actualizar contador
            totalFormsInput.value = (totalForms + 1).toString();
            
            // Añadir evento al botón eliminar
            const btnEliminar = nuevoBloque.querySelector('button');
            if (btnEliminar) {
                btnEliminar.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    manejarEliminacionImagen(this);
                });
            }
            
            // Añadir vista previa al seleccionar imagen
            const inputFile = nuevoBloque.querySelector('input[type="file"]');
            if (inputFile) {
                inputFile.addEventListener('change', function() {
                    if (this.files && this.files[0]) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            // Crear contenedor de vista previa
                            let preview = nuevoBloque.querySelector('.image-preview');
                            if (!preview) {
                                preview = document.createElement('div');
                                preview.className = 'image-preview';
                                preview.style.textAlign = 'center';
                                preview.style.marginBottom = '10px';
                                nuevoBloque.prepend(preview);
                            }
                            
                            // Crear o actualizar imagen
                            let img = preview.querySelector('img');
                            if (!img) {
                                img = document.createElement('img');
                                preview.appendChild(img);
                            }
                            
                            // Establecer atributos de imagen
                            img.src = e.target.result;
                            img.alt = 'Vista previa';
                            img.style.maxWidth = '100%';
                            img.style.maxHeight = '150px';
                        };
                        reader.readAsDataURL(this.files[0]);
                    }
                });
            }
            
            console.log('Nueva imagen añadida con éxito');
        } catch (error) {
            console.error('Error al añadir nueva imagen:', error);
            isProcessing = false;
        }
    }
    
    /**
     * Maneja la eliminación de una imagen
     */
    function manejarEliminacionImagen(boton) {
        // Evitar procesamientos múltiples
        if (isProcessing) return;
        isProcessing = true;
        
        // Encontrar el bloque padre que contiene toda la imagen
        const bloque = boton.closest('.imagen-form') || boton.closest('[id^="imagenes-"]');
        
        if (!bloque) {
            console.error('No se pudo encontrar el bloque padre para eliminar');
            isProcessing = false;
            return;
        }
        
        // Confirmar eliminación
        if (confirm('¿Estás seguro de eliminar esta imagen?')) {
            console.log('Eliminando imagen...');
            
            // Buscar checkbox DELETE para imágenes existentes
            const checkboxDelete = bloque.querySelector('input[name$="-DELETE"]');
            
            if (checkboxDelete) {
                // Es una imagen existente: marcar para eliminación
                checkboxDelete.checked = true;
                
                // Aplicar estilo visual
                Object.assign(bloque.style, {
                    opacity: '0.5',
                    backgroundColor: '#fff8f8',
                    borderStyle: 'dashed',
                    borderColor: '#dc3545'
                });
                
                // Cambiar botón a "Restaurar"
                boton.textContent = 'Restaurar';
                boton.classList.remove('btn-danger');
                boton.classList.add('btn-warning');
                
                // Añadir nuevo evento para restaurar
                boton.removeEventListener('click', manejarEliminacionImagen);
                boton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Desmarcar checkbox
                    checkboxDelete.checked = false;
                    
                    // Restaurar apariencia
                    Object.assign(bloque.style, {
                        opacity: '1',
                        backgroundColor: '#fff',
                        borderStyle: 'solid',
                        borderColor: '#dee2e6'
                    });
                    
                    // Restaurar botón
                    boton.textContent = 'Eliminar imagen';
                    boton.classList.remove('btn-warning');
                    boton.classList.add('btn-danger');
                    
                    // Restaurar evento original
                    const nuevoBoton = boton.cloneNode(true);
                    boton.parentNode.replaceChild(nuevoBoton, boton);
                    nuevoBoton.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        manejarEliminacionImagen(this);
                    });
                });
            } else {
                // Es una imagen nueva: eliminar completamente
                bloque.remove();
                
                // Actualizar contador y reindexar
                actualizarIndices();
            }
        }
        
        // Permitir nuevas operaciones
        isProcessing = false;
    }
    
    /**
     * Actualiza los índices de todos los formularios
     */
    function actualizarIndices() {
        const forms = contenedor.querySelectorAll('.imagen-form, [id^="imagenes-"]');
        
        // Actualizar contador total
        totalFormsInput.value = forms.length;
        
        // Reindexar todos los formularios
        forms.forEach((form, index) => {
            // Actualizar inputs
            form.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name && input.name.match(new RegExp(`^${prefix}-\\d+`))) {
                    input.name = input.name.replace(
                        new RegExp(`^${prefix}-\\d+`), 
                        `${prefix}-${index}`
                    );
                }
                
                if (input.id && input.id.match(new RegExp(`^id_${prefix}-\\d+`))) {
                    input.id = input.id.replace(
                        new RegExp(`^id_${prefix}-\\d+`), 
                        `id_${prefix}-${index}`
                    );
                }
            });
            
            // Actualizar labels
            form.querySelectorAll('label').forEach(label => {
                if (label.htmlFor && label.htmlFor.match(new RegExp(`^id_${prefix}-\\d+`))) {
                    label.htmlFor = label.htmlFor.replace(
                        new RegExp(`^id_${prefix}-\\d+`), 
                        `id_${prefix}-${index}`
                    );
                }
            });
        });
        
        console.log(`Índices actualizados. Total: ${forms.length}`);
    }
});