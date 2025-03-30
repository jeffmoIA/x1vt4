/**
 * Script simplificado para gestión de imágenes
 * Enfocado en resolver el problema del botón añadir
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando script simplificado de imágenes...');
    
    // Referencias a elementos clave
    const addButton = document.querySelector('button[id="add-imagen"]');
    const imagenContainer = document.getElementById('imagenes-container');
    const totalFormsInput = document.querySelector('input[name="imagenes-TOTAL_FORMS"]');
    
    // Verificar si se encontraron los elementos
    console.log('Botón añadir:', addButton);
    console.log('Contenedor imágenes:', imagenContainer);
    console.log('Input TOTAL_FORMS:', totalFormsInput);
    
    // Si no se encuentra el botón por ID, intentar por texto
    if (!addButton) {
        console.log('Buscando botón por texto...');
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.textContent.includes('Añadir')) {
                addButton = btn;
                console.log('Botón encontrado por texto:', btn);
                break;
            }
        }
    }
    
    // Asignar evento al botón de añadir imagen
    if (addButton) {
        addButton.addEventListener('click', function() {
            console.log('Botón añadir imagen clickeado');
            
            // Obtener número actual de formularios
            const formCount = totalFormsInput ? parseInt(totalFormsInput.value) : 0;
            const newIndex = formCount;
            console.log(`Añadiendo imagen #${newIndex}`);
            
            // Crear nuevo bloque de imagen
            const nuevoBloque = document.createElement('div');
            nuevoBloque.className = 'imagen-form';
            nuevoBloque.style.border = '1px solid #ddd';
            nuevoBloque.style.padding = '15px';
            nuevoBloque.style.margin = '10px 0';
            nuevoBloque.style.borderRadius = '5px';
            
            // HTML para el nuevo bloque
            nuevoBloque.innerHTML = `
                <div style="margin-bottom:10px;">
                    <label>Imagen</label>
                    <input type="file" name="imagenes-${newIndex}-imagen" 
                           id="id_imagenes-${newIndex}-imagen" class="form-control">
                </div>
                <div style="margin-bottom:10px;">
                    <label>Orden</label>
                    <input type="number" name="imagenes-${newIndex}-orden" 
                           id="id_imagenes-${newIndex}-orden" value="${newIndex}" class="form-control">
                </div>
                <div style="margin-bottom:10px;">
                    <input type="checkbox" name="imagenes-${newIndex}-es_principal" 
                           id="id_imagenes-${newIndex}-es_principal">
                    <label for="id_imagenes-${newIndex}-es_principal">Es imagen principal</label>
                </div>
                <div style="margin-bottom:10px;">
                    <label>Título (opcional)</label>
                    <input type="text" name="imagenes-${newIndex}-titulo" 
                           id="id_imagenes-${newIndex}-titulo" class="form-control">
                </div>
                <button type="button" class="btn btn-danger btn-eliminar-imagen" style="width:100%">
                    <i class="fas fa-trash"></i> Eliminar imagen
                </button>
            `;
            
            // Añadir al contenedor
            if (imagenContainer) {
                imagenContainer.appendChild(nuevoBloque);
                
                // Actualizar contador
                if (totalFormsInput) {
                    totalFormsInput.value = (formCount + 1).toString();
                    console.log(`TOTAL_FORMS actualizado a ${formCount + 1}`);
                }
                
                // Asignar evento al botón eliminar
                const eliminarBtn = nuevoBloque.querySelector('.btn-eliminar-imagen');
                if (eliminarBtn) {
                    eliminarBtn.addEventListener('click', function() {
                        if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                            nuevoBloque.remove();
                            
                            // Actualizar contador
                            if (totalFormsInput) {
                                const currentCount = parseInt(totalFormsInput.value);
                                totalFormsInput.value = (currentCount - 1).toString();
                                console.log(`TOTAL_FORMS actualizado a ${currentCount - 1}`);
                            }
                            
                            // Reindexar formularios
                            actualizarIndicesFormularios();
                        }
                    });
                }
            } else {
                console.error('No se pudo encontrar el contenedor de imágenes');
            }
        });
        console.log('Evento click asignado al botón añadir imagen');
    } else {
        console.error('No se pudo encontrar el botón de añadir imagen');
    }
    
    // Función para reindexar formularios
    function actualizarIndicesFormularios() {
        if (!imagenContainer || !totalFormsInput) return;
        
        const forms = imagenContainer.querySelectorAll('.imagen-form');
        totalFormsInput.value = forms.length.toString();
        
        forms.forEach((form, index) => {
            form.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name && input.name.includes('imagenes-')) {
                    const newName = input.name.replace(/imagenes-\d+/, `imagenes-${index}`);
                    input.name = newName;
                }
                if (input.id && input.id.includes('id_imagenes-')) {
                    const newId = input.id.replace(/id_imagenes-\d+/, `id_imagenes-${index}`);
                    input.id = newId;
                }
            });
            
            form.querySelectorAll('label[for]').forEach(label => {
                if (label.htmlFor && label.htmlFor.includes('id_imagenes-')) {
                    const newFor = label.htmlFor.replace(/id_imagenes-\d+/, `id_imagenes-${index}`);
                    label.htmlFor = newFor;
                }
            });
        });
    }
    
    // Configurar botones de eliminar existentes
    const botonesEliminar = document.querySelectorAll('.btn-eliminar-imagen');
    botonesEliminar.forEach(btn => {
        btn.addEventListener('click', function() {
            const bloque = btn.closest('.imagen-form');
            if (bloque && confirm('¿Estás seguro de eliminar esta imagen?')) {
                // Verificar si hay un checkbox DELETE para marcar
                const deleteCheck = bloque.querySelector('input[name$="-DELETE"]');
                if (deleteCheck) {
                    // Es una imagen existente, solo marcar para eliminar
                    deleteCheck.checked = true;
                    bloque.style.opacity = '0.5';
                    bloque.style.border = '1px dashed #dc3545';
                    bloque.style.backgroundColor = '#fff4f4';
                    
                    // Cambiar texto del botón
                    btn.className = 'btn btn-warning btn-eliminar-imagen';
                    btn.innerHTML = '<i class="fas fa-undo"></i> Restaurar';
                    
                    // Nuevo manejador para restaurar
                    btn.removeEventListener('click', arguments.callee);
                    btn.addEventListener('click', function() {
                        deleteCheck.checked = false;
                        bloque.style.opacity = '1';
                        bloque.style.border = '1px solid #ddd';
                        bloque.style.backgroundColor = '';
                        
                        // Restaurar botón
                        btn.className = 'btn btn-danger btn-eliminar-imagen';
                        btn.innerHTML = '<i class="fas fa-trash"></i> Eliminar imagen';
                        
                        // Restaurar evento original
                        btn.removeEventListener('click', arguments.callee);
                        const newBtn = btn.cloneNode(true);
                        btn.parentNode.replaceChild(newBtn, btn);
                        newBtn.addEventListener('click', function() {
                            if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                                const bloqueActual = newBtn.closest('.imagen-form');
                                const deleteCheckActual = bloqueActual.querySelector('input[name$="-DELETE"]');
                                
                                if (deleteCheckActual) {
                                    deleteCheckActual.checked = true;
                                    bloqueActual.style.opacity = '0.5';
                                    bloqueActual.style.border = '1px dashed #dc3545';
                                    bloqueActual.style.backgroundColor = '#fff4f4';
                                    
                                    // Cambiar texto del botón de nuevo
                                    newBtn.className = 'btn btn-warning btn-eliminar-imagen';
                                    newBtn.innerHTML = '<i class="fas fa-undo"></i> Restaurar';
                                }
                            }
                        });
                    });
                } else {
                    // Es una imagen nueva, eliminar directamente
                    bloque.remove();
                    
                    // Actualizar contador
                    if (totalFormsInput) {
                        const currentCount = parseInt(totalFormsInput.value);
                        totalFormsInput.value = (currentCount - 1).toString();
                    }
                    
                    // Reindexar formularios
                    actualizarIndicesFormularios();
                }
            }
        });
    });
});