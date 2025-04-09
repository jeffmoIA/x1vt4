/**
 * crear_producto_imagenes.js - Gestión de imágenes para el formulario de creación de productos
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando gestor de imágenes para creación de producto');
    
    // Buscar el botón de añadir imagen (usando múltiples selectores para mayor seguridad)
    const addImagenBtn = 
        document.querySelector('button[id="add-imagen"]') || 
        document.querySelector('button:contains("Añadir otra imagen")') ||
        document.querySelector('button:contains("Añadir imagen")') ||
        document.querySelector('.btn-primary[id*="imagen"]');
    
    // Si no encuentra con los selectores, buscar entre todos los botones primarios
    if (!addImagenBtn) {
        const buttons = document.querySelectorAll('.btn-primary');
        for (const btn of buttons) {
            if (btn.textContent.includes('imagen') || btn.textContent.includes('Imagen')) {
                console.log('Botón encontrado por contenido de texto:', btn.textContent);
                applyButtonLogic(btn);
                return;
            }
        }
        console.error('No se pudo encontrar el botón para añadir imágenes');
        return;
    } else {
        console.log('Botón encontrado:', addImagenBtn.outerHTML);
        applyButtonLogic(addImagenBtn);
    }
    
    // Función para aplicar la lógica al botón encontrado
    function applyButtonLogic(button) {
        // Encontrar el contenedor y el campo TOTAL_FORMS
        const imagenesContainer = document.getElementById('imagenes-container');
        const totalFormsInput = document.querySelector('[name="imagenes-TOTAL_FORMS"]');
        
        if (!imagenesContainer || !totalFormsInput) {
            console.error('No se encontró el contenedor o el campo TOTAL_FORMS');
            console.log('Elementos encontrados en el formulario:');
            document.querySelectorAll('div[id], input[name]').forEach(el => 
                console.log(el.tagName, el.id || el.name, el.outerHTML.substring(0, 100) + '...')
            );
            return;
        }
        
        // Eliminar eventos previos con un clon
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        
        // Añadir el evento de clic
        newBtn.addEventListener('click', function() {
            console.log('Botón de añadir imagen clickeado');
            
            // Obtener número actual de formularios
            const formCount = parseInt(totalFormsInput.value);
            
            // Buscar una plantilla de formulario
            const formTemplate = document.querySelector('.imagen-form');
            if (!formTemplate) {
                console.error('No se encontró plantilla para el formulario de imagen');
                return;
            }
            
            // Crear nuevo formulario
            const newForm = formTemplate.cloneNode(true);
            
            // Asignar ID para referencia
            newForm.id = `imagen-form-${formCount}`;
            
            // Actualizar índices
            newForm.innerHTML = newForm.innerHTML
                .replace(/imagenes-\d+-/g, `imagenes-${formCount}-`)
                .replace(/id_imagenes-\d+-/g, `id_imagenes-${formCount}-`);
            
            // Limpiar valores
            newForm.querySelectorAll('input[type="text"], input[type="number"]').forEach(input => {
                if (input.name.includes('orden')) {
                    input.value = formCount;
                } else {
                    input.value = '';
                }
            });
            
            // Reiniciar input de archivo
            const fileInput = newForm.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.value = '';
            }
            
            // Desmarcar checkbox
            const checkbox = newForm.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = false;
            }
            
            // Configurar botón eliminar
            const deleteBtn = newForm.querySelector('.btn-eliminar-imagen');
            if (deleteBtn) {
                const newDeleteBtn = deleteBtn.cloneNode(true);
                if (deleteBtn.parentNode) {
                    deleteBtn.parentNode.replaceChild(newDeleteBtn, deleteBtn);
                }
                
                newDeleteBtn.addEventListener('click', function() {
                    if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                        newForm.remove();
                    }
                });
            }
            
            // Añadir nuevo formulario
            imagenesContainer.appendChild(newForm);
            
            // Incrementar contador
            totalFormsInput.value = formCount + 1;
            
            console.log('Nueva imagen añadida correctamente');
        });
        
        // Configurar botones eliminar existentes
        document.querySelectorAll('.btn-eliminar-imagen').forEach(btn => {
            const newDelBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newDelBtn, btn);
            
            newDelBtn.addEventListener('click', function() {
                if (confirm('¿Estás seguro de eliminar esta imagen?')) {
                    this.closest('.imagen-form').remove();
                }
            });
        });
    }
    
    console.log('Gestor de imágenes inicializado correctamente');
});