/**
 * Gestor de imágenes simplificado - Solución directa para problemas de UI
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando gestor de imágenes simplificado...');
    
    // Referencias a elementos del DOM
    const contenedor = document.getElementById('imagenes-container');
    const totalFormsInput = document.querySelector('input[name="imagenes-TOTAL_FORMS"]');
    
    // Encontrar botón añadir usando varios métodos
    let botonAnadir = document.getElementById('add-imagen');
    if (!botonAnadir) {
        // Intentar encontrar por texto o clase
        document.querySelectorAll('button, a.btn').forEach(btn => {
            if (btn.textContent.includes('Añadir') || 
                btn.textContent.includes('añadir') || 
                btn.textContent.includes('agregar') || 
                btn.textContent.includes('Agregar')) {
                botonAnadir = btn;
            }
        });
    }
    
    // Verificar que elementos necesarios existen
    if (!contenedor) {
        console.error('Error: No se encontró el contenedor de imágenes (#imagenes-container)');
        return;
    }
    
    if (!totalFormsInput) {
        console.error('Error: No se encontró el input de TOTAL_FORMS');
        return;
    }
    
    if (!botonAnadir) {
        console.error('Error: No se encontró el botón para añadir imágenes');
        return;
    }
    
    console.log('Elementos encontrados correctamente:', {
        contenedor: contenedor,
        totalForms: totalFormsInput,
        botonAnadir: botonAnadir
    });
    
    // 1. Mejorar apariencia de elementos existentes
    mejorarApariencia();
    
    // 2. Configurar botones de eliminar existentes
    configurarBotonesEliminar();
    
    // 3. Configurar botón añadir imagen
    botonAnadir.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Click en botón añadir');
        
        // Prevenir múltiples clicks
        if (this.disabled) return;
        this.disabled = true;
        
        // Añadir nueva imagen
        anadirNuevaImagen();
        
        // Re-habilitar después de un breve retraso
        setTimeout(() => {
            this.disabled = false;
        }, 500);
    });
    
    /**
     * Mejora la apariencia de los elementos de imagen existentes
     */
    function mejorarApariencia() {
        // Obtener todos los bloques de imagen
        const bloques = contenedor.querySelectorAll('.imagen-form, [class*="imagen"]');
        
        // Aplicar estilos para mejorar apariencia
        bloques.forEach(bloque => {
            // Asegurar que tenga la clase correcta
            bloque.classList.add('imagen-form');
            
            // Aplicar estilos directamente
            bloque.style.padding = '15px';
            bloque.style.margin = '10px';
            bloque.style.border = '1px solid #dee2e6';
            bloque.style.borderRadius = '5px';
            bloque.style.backgroundColor = '#fff';
            bloque.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
            bloque.style.width = '300px';
            bloque.style.display = 'inline-block';
            bloque.style.verticalAlign = 'top';
            
            // Mejorar imagen si existe
            const imagen = bloque.querySelector('img');
            if (imagen) {
                imagen.style.maxWidth = '100%';
                imagen.style.height = 'auto';
                imagen.style.display = 'block';
                imagen.style.margin = '0 auto 15px auto';
                imagen.style.maxHeight = '150px';
            }
            
            // Mejorar inputs
            bloque.querySelectorAll('input, select, textarea').forEach(input => {
                if (!input.classList.contains('form-control') && input.type !== 'checkbox') {
                    input.classList.add('form-control');
                    input.style.marginBottom = '10px';
                }
                
                // Mejorar checkbox
                if (input.type === 'checkbox') {
                    const label = input.nextElementSibling;
                    if (label && label.tagName === 'LABEL') {
                        // Crear contenedor para mejor alineación
                        const checkContainer = document.createElement('div');
                        checkContainer.className = 'form-check mb-3';
                        
                        // Configurar checkbox
                        input.className = 'form-check-input';
                        label.className = 'form-check-label';
                        
                        // Mover elementos al nuevo contenedor
                        const parent = input.parentNode;
                        checkContainer.appendChild(input);
                        checkContainer.appendChild(label);
                        parent.appendChild(checkContainer);
                    }
                }
            });
        });
    }
    
    /**
     * Configura los botones de eliminar para cada bloque de imagen
     */
    function configurarBotonesEliminar() {
        // Encontrar todos los botones de eliminar
        const botonesEliminar = contenedor.querySelectorAll('button, .btn-eliminar-imagen, [class*="eliminar"]');
        
        botonesEliminar.forEach(boton => {
            if (boton.textContent.includes('Eliminar') || 
                boton.textContent.includes('eliminar') ||
                boton.innerHTML.includes('trash')) {
                
                // Remover listeners previos clonando el botón
                const nuevoBoton = boton.cloneNode(true);
                boton.parentNode.replaceChild(nuevoBoton, boton);
                
                // Aplicar estilo consistente
                nuevoBoton.className = 'btn btn-danger btn-eliminar-imagen';
                nuevoBoton.style.width = '100%';
                nuevoBoton.style.marginTop = '15px';
                
                // Asignar nuevo evento
                nuevoBoton.addEventListener('click', function(e) {
                    e.preventDefault();
                    manejarEliminacion(this);
                });
            }
        });
    }
    
    /**
     * Maneja la eliminación de un bloque de imagen
     */
    function manejarEliminacion(boton) {
        // Encontrar el bloque padre
        const bloque = boton.closest('.imagen-form') || boton.parentElement.parentElement;
        
        if (!bloque) {
            console.error('No se pudo encontrar el bloque de imagen a eliminar');
            return;
        }
        
        // Confirmar eliminación
        if (confirm('¿Estás seguro de eliminar esta imagen?')) {
            // Buscar checkbox DELETE para imágenes existentes
            const checkboxDelete = bloque.querySelector('input[name*="DELETE"]');
            
            if (checkboxDelete) {
                // Es imagen existente, marcar para eliminar
                checkboxDelete.checked = true;
                
                // Aplicar estilo "eliminado"
                bloque.style.opacity = '0.5';
                bloque.style.backgroundColor = '#ffeeee';
                bloque.style.border = '1px dashed #dc3545';
                
                // Cambiar botón a "Restaurar"
                boton.textContent = 'Restaurar';
                boton.className = 'btn btn-warning';
                
                // Nuevo evento para restaurar
                boton.removeEventListener('click', arguments.callee);
                boton.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Desmarcar checkbox
                    checkboxDelete.checked = false;
                    
                    // Restaurar apariencia
                    bloque.style.opacity = '';
                    bloque.style.backgroundColor = '';
                    bloque.style.border = '';
                    
                    // Restaurar botón
                    boton.textContent = 'Eliminar imagen';
                    boton.className = 'btn btn-danger btn-eliminar-imagen';
                    
                    // Restaurar evento original
                    boton.removeEventListener('click', arguments.callee);
                    boton.addEventListener('click', function(e) {
                        e.preventDefault();
                        manejarEliminacion(this);
                    });
                });
            } else {
                // Es imagen nueva, eliminar del DOM
                bloque.remove();
                
                // Actualizar contador de formularios
                actualizarContador();
            }
        }
    }
    
    /**
     * Añade una nueva imagen al formulario
     */
    function anadirNuevaImagen() {
        try {
            // Obtener índice para el nuevo formulario
            const formCount = parseInt(totalFormsInput.value || '0');
            console.log(`Añadiendo nueva imagen con índice ${formCount}`);
            
            // Crear el nuevo bloque
            const nuevoBloque = document.createElement('div');
            nuevoBloque.className = 'imagen-form';
            nuevoBloque.style.padding = '15px';
            nuevoBloque.style.margin = '10px';
            nuevoBloque.style.border = '1px solid #dee2e6';
            nuevoBloque.style.borderRadius = '5px';
            nuevoBloque.style.backgroundColor = '#fff';
            nuevoBloque.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
            nuevoBloque.style.width = '300px';
            nuevoBloque.style.display = 'inline-block';
            nuevoBloque.style.verticalAlign = 'top';
            
            // HTML del nuevo bloque
            nuevoBloque.innerHTML = `
                <label class="form-label">Imagen</label>
                <input type="file" name="imagenes-${formCount}-imagen" 
                       id="id_imagenes-${formCount}-imagen" 
                       class="form-control mb-3" accept="image/*">
                
                <label class="form-label">Orden</label>
                <input type="number" name="imagenes-${formCount}-orden" 
                       id="id_imagenes-${formCount}-orden" 
                       value="${formCount}" class="form-control mb-3">
                
                <div class="form-check mb-3">
                    <input type="checkbox" name="imagenes-${formCount}-es_principal" 
                           id="id_imagenes-${formCount}-es_principal" 
                           class="form-check-input">
                    <label for="id_imagenes-${formCount}-es_principal" class="form-check-label">
                        Es imagen principal
                    </label>
                </div>
                
                <label class="form-label">Título (opcional)</label>
                <input type="text" name="imagenes-${formCount}-titulo" 
                       id="id_imagenes-${formCount}-titulo" 
                       class="form-control mb-3">
                
                <button type="button" class="btn btn-danger btn-eliminar-imagen" style="width:100%">
                    Eliminar imagen
                </button>
            `;
            
            // Añadir al contenedor
            contenedor.appendChild(nuevoBloque);
            
            // Actualizar contador
            totalFormsInput.value = (formCount + 1).toString();
            
            // Configurar evento del nuevo botón eliminar
            const botonEliminar = nuevoBloque.querySelector('.btn-eliminar-imagen');
            if (botonEliminar) {
                botonEliminar.addEventListener('click', function(e) {
                    e.preventDefault();
                    manejarEliminacion(this);
                });
            }
            
            // Mostrar vista previa cuando se seleccione una imagen
            const inputImagen = nuevoBloque.querySelector('input[type="file"]');
            if (inputImagen) {
                inputImagen.addEventListener('change', function() {
                    if (this.files && this.files[0]) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            // Verificar si ya existe vista previa
                            let preview = nuevoBloque.querySelector('.image-preview');
                            if (!preview) {
                                preview = document.createElement('div');
                                preview.className = 'image-preview';
                                preview.style.textAlign = 'center';
                                preview.style.marginBottom = '15px';
                                nuevoBloque.insertBefore(preview, nuevoBloque.firstChild);
                            }
                            
                            // Crear o actualizar imagen
                            let img = preview.querySelector('img');
                            if (!img) {
                                img = document.createElement('img');
                                img.alt = 'Vista previa';
                                img.style.maxWidth = '100%';
                                img.style.maxHeight = '150px';
                                preview.appendChild(img);
                            }
                            
                            img.src = e.target.result;
                        }
                        reader.readAsDataURL(this.files[0]);
                    }
                });
            }
            
            console.log('Nueva imagen añadida correctamente');
        } catch (error) {
            console.error('Error al añadir nueva imagen:', error);
        }
    }
    
    /**
     * Actualiza el contador de formularios
     */
    function actualizarContador() {
        const forms = contenedor.querySelectorAll('.imagen-form');
        totalFormsInput.value = forms.length.toString();
        console.log(`Contador actualizado: ${forms.length} imágenes`);
    }
});