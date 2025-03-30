// Script para corregir funcionalidad de botones en el formulario de producto
document.addEventListener('DOMContentLoaded', function() {
    // Convierte los checkboxes DELETE de tallas en botones de eliminar
    function convertirCheckboxesEnBotones() {
        document.querySelectorAll('.talla-form').forEach(function(tallaForm) {
            // Evitar duplicación verificando si ya existe un botón de eliminar
            if (tallaForm.querySelector('.btn-eliminar-talla')) return;
            
            // Buscar el checkbox DELETE
            const deleteCheckbox = tallaForm.querySelector('input[name$="-DELETE"]');
            if (!deleteCheckbox) return;
            
            // Ocultar el div del checkbox
            const checkboxContainer = deleteCheckbox.closest('.form-check');
            if (checkboxContainer) checkboxContainer.style.display = 'none';
            
            // Crear botón de eliminar
            const btnEliminar = document.createElement('button');
            btnEliminar.type = 'button';
            btnEliminar.className = 'btn btn-sm btn-danger btn-eliminar-talla';
            btnEliminar.innerHTML = '<i class="fas fa-trash"></i> Eliminar';
            
            // Añadir evento click que funcione tanto para elementos nuevos como existentes
            btnEliminar.addEventListener('click', function() {
                if (confirm('¿Estás seguro de eliminar esta talla?')) {
                    // Si la talla no tiene ID (es nueva), simplemente eliminarla del DOM
                    const idInput = tallaForm.querySelector('input[name$="-id"]');
                    if (!idInput || !idInput.value) {
                        tallaForm.remove();
                        // Actualizar el contador
                        const totalForms = document.querySelector('input[name="tallas-TOTAL_FORMS"]');
                        if (totalForms) {
                            totalForms.value = parseInt(totalForms.value) - 1;
                        }
                    } else {
                        // Si ya existe en la BD, marcarla para eliminación
                        deleteCheckbox.checked = true;
                        tallaForm.style.display = 'none';
                    }
                }
            });
            
            // Añadir botón a la talla
            tallaForm.querySelector('td:last-child').appendChild(btnEliminar);
        });
    }
    
    // Ejecutar la conversión cuando carga la página
    convertirCheckboxesEnBotones();
    
    // Botón para añadir talla - utilizando un manejador único
    const btnAddTalla = document.getElementById('add-talla');
    if (btnAddTalla) {
        // Remover eventos anteriores para evitar duplicación
        const newBtn = btnAddTalla.cloneNode(true);
        btnAddTalla.parentNode.replaceChild(newBtn, btnAddTalla);
        
        newBtn.addEventListener('click', function() {
            // Obtener formset para tallas
            const tallaFormset = document.getElementById('tallas-container');
            const totalForms = document.querySelector('input[name="tallas-TOTAL_FORMS"]');
            
            if (!tallaFormset || !totalForms) {
                console.error('No se encontraron elementos necesarios para añadir talla');
                return;
            }
            
            // Obtener total actual de formularios
            const formCount = parseInt(totalForms.value);
            
            // Obtener template de la primera talla (como base)
            const tallaTemplate = tallaFormset.querySelector('.talla-form');
            if (!tallaTemplate) {
                console.error('No se encontró template para talla');
                return;
            }
            
            // Clonar template
            const newTalla = tallaTemplate.cloneNode(true);
            
            // Remover botón eliminar existente (si lo hay)
            const oldBtn = newTalla.querySelector('.btn-eliminar-talla');
            if (oldBtn) oldBtn.remove();
            
            // Actualizar IDs y nombres
            const inputs = newTalla.querySelectorAll('input, select');
            inputs.forEach(input => {
                const name = input.getAttribute('name');
                if (name) {
                    // Reemplazar índice en el nombre e ID
                    const newName = name.replace(/tallas-\d+/, `tallas-${formCount}`);
                    input.setAttribute('name', newName);
                    
                    const id = input.getAttribute('id');
                    if (id) {
                        const newId = id.replace(/id_tallas-\d+/, `id_tallas-${formCount}`);
                        input.setAttribute('id', newId);
                    }
                }
                
                // Limpiar valores
                if (input.type !== 'checkbox' && input.type !== 'hidden') {
                    input.value = '';
                } else if (input.type === 'checkbox') {
                    input.checked = false;
                }
            });
            
            // Actualizar labels
            const labels = newTalla.querySelectorAll('label');
            labels.forEach(label => {
                const forAttr = label.getAttribute('for');
                if (forAttr) {
                    const newFor = forAttr.replace(/id_tallas-\d+/, `id_tallas-${formCount}`);
                    label.setAttribute('for', newFor);
                }
            });
            
            // Añadir al contenedor
            tallaFormset.appendChild(newTalla);
            
            // Actualizar contador
            totalForms.value = formCount + 1;
            
            // Convertir checkbox a botón en la nueva talla
            convertirCheckboxesEnBotones();
        });
    }
    
    // Botón para añadir imagen
    const btnAddImagen = document.getElementById('add-imagen');
    if (btnAddImagen) {
        // Remover eventos anteriores para evitar duplicación
        const newBtnImg = btnAddImagen.cloneNode(true);
        btnAddImagen.parentNode.replaceChild(newBtnImg, btnAddImagen);
        
        newBtnImg.addEventListener('click', function() {
            // Obtener formset para imágenes
            const imagenesContainer = document.getElementById('imagenes-container');
            const totalForms = document.querySelector('input[name="imagenes-TOTAL_FORMS"]');
            
            if (!imagenesContainer || !totalForms) {
                console.error('No se encontraron elementos necesarios para añadir imagen');
                return;
            }
            
            // Obtener total actual de formularios
            const formCount = parseInt(totalForms.value);
            
            // Crear nuevo formulario de imagen
            const newImagen = document.createElement('div');
            newImagen.className = 'imagen-form col-md-4 mb-4';
            newImagen.id = `imagenes-${formCount}`;
            
            // HTML para el nuevo formulario de imagen
            newImagen.innerHTML = `
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>Imagen nueva</span>
                    </div>
                    <div class="card-body">
                        <input type="hidden" name="imagenes-${formCount}-id" id="id_imagenes-${formCount}-id">
                        <input type="hidden" name="imagenes-${formCount}-DELETE" id="id_imagenes-${formCount}-DELETE">
                
                <div class="mb-3">
                    <label for="id_imagenes-${formCount}-imagen" class="form-label">Imagen</label>
                    <input type="file" name="imagenes-${formCount}-imagen" class="form-control" id="id_imagenes-${formCount}-imagen" accept="image/*">
                </div>
                
                <div class="mb-3">
                    <label for="id_imagenes-${formCount}-orden" class="form-label">Orden</label>
                    <input type="number" name="imagenes-${formCount}-orden" class="form-control" id="id_imagenes-${formCount}-orden" value="${Date.now() % 10000}">
                </div>
                
                <div class="form-check mb-3">
                    <input type="checkbox" name="imagenes-${formCount}-es_principal" class="form-check-input" id="id_imagenes-${formCount}-es_principal">
                    <label for="id_imagenes-${formCount}-es_principal" class="form-check-label">Es imagen principal</label>
                </div>
                
                <div class="mb-3">
                    <label for="id_imagenes-${formCount}-titulo" class="form-label">Título (opcional)</label>
                    <input type="text" name="imagenes-${formCount}-titulo" class="form-control" id="id_imagenes-${formCount}-titulo" placeholder="Título descriptivo para SEO y accesibilidad">
                </div>
                
                <div class="card-footer text-center">
                        <button type="button" class="btn btn-danger btn-eliminar-imagen">
                            <i class="fas fa-trash"></i> Eliminar
                        </button>
                    </div>
                </div>
            `;
            
            // Añadir al contenedor
            imagenesContainer.appendChild(newImagen);
            
            // Actualizar contador
            totalForms.value = formCount + 1;
            
            // Añadir event listener para el botón de eliminar
            const btnEliminar = newImagen.querySelector('.btn-eliminar-imagen');
            if (btnEliminar) {
                btnEliminar.addEventListener('click', function() {
                    if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                        newImagen.remove();
                        // Actualizar el contador
                        totalForms.value = parseInt(totalForms.value) - 1;
                    }
                });
            }
        });
    }
    
    // Manejar botones existentes para eliminar imágenes
    document.querySelectorAll('.btn-eliminar-imagen').forEach(btn => {
        btn.addEventListener('click', function() {
            const imagenForm = this.closest('.imagen-form');
            if (!imagenForm) return;
            
            if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                const index = imagenForm.id.split('-')[1];
                const deleteInput = document.getElementById(`id_imagenes-${index}-DELETE`);
                
                if (deleteInput) {
                    // Marcar para eliminación
                    deleteInput.value = 'on';
                    // Ocultar visualmente
                    imagenForm.style.display = 'none';
                }
            }
        });
    });
});