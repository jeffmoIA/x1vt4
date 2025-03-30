// Función para manejar la eliminación de imágenes del formulario
document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando funcionalidad de eliminación de imágenes');
    
    // 1. Identificar todas las imágenes en el formulario (cualquier formato)
    const imagenes = document.querySelectorAll('.image-thumbnail, .img-thumbnail, img[src*="media/productos"]');
    console.log('Imágenes encontradas:', imagenes.length);
    
    // 2. Para cada imagen, añadir la funcionalidad
    imagenes.forEach(function(imagen) {
        // Asegurar que la imagen sea clickeable
        imagen.style.cursor = 'pointer';
        
        // Encontrar el contenedor padre que contiene toda la estructura de la imagen
        const contenedorImagen = imagen.closest('div');
        if (!contenedorImagen) return;
        
        // Crear elementos para confirmar/cancelar eliminación
        const overlay = document.createElement('div');
        overlay.className = 'delete-overlay';
        overlay.style.cssText = 'display:none; position:absolute; top:0; left:0; width:100%; height:100%; background-color:rgba(0,0,0,0.7); z-index:100; align-items:center; justify-content:center;';
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = 'display:flex; gap:10px;';
        
        const confirmarBtn = document.createElement('button');
        confirmarBtn.type = 'button';
        confirmarBtn.className = 'btn btn-success btn-sm';
        confirmarBtn.innerHTML = '<i class="fas fa-check"></i>';
        confirmarBtn.title = 'Confirmar eliminación';
        
        const cancelarBtn = document.createElement('button');
        cancelarBtn.type = 'button';
        cancelarBtn.className = 'btn btn-danger btn-sm';
        cancelarBtn.innerHTML = '<i class="fas fa-times"></i>';
        cancelarBtn.title = 'Cancelar eliminación';
        
        buttonContainer.appendChild(confirmarBtn);
        buttonContainer.appendChild(cancelarBtn);
        overlay.appendChild(buttonContainer);
        
        // Insertar el overlay en el contenedor
        contenedorImagen.style.position = 'relative';
        contenedorImagen.appendChild(overlay);
        
        // Configurar evento de clic en la imagen
        imagen.addEventListener('click', function(e) {
            e.preventDefault();
            overlay.style.display = 'flex';
            console.log('Mostrando opciones de eliminación');
        });
        
        // Configurar evento de confirmación
        confirmarBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Buscar el checkbox DELETE más cercano
            const deleteCheckbox = contenedorImagen.querySelector('input[id*="DELETE"]');
            if (deleteCheckbox) {
                // Marcar para eliminar
                deleteCheckbox.checked = true;
                
                // Aplicar estilo visual
                imagen.style.opacity = '0.5';
                overlay.style.display = 'none';
                
                // Añadir indicador visual
                const indicator = document.createElement('div');
                indicator.style.cssText = 'position:absolute; bottom:0; left:0; right:0; background-color:#dc3545; color:white; font-size:12px; text-align:center; padding:2px;';
                indicator.textContent = 'Se eliminará al guardar';
                contenedorImagen.appendChild(indicator);
                
                console.log('Imagen marcada para eliminar');
            } else {
                // Si no encontramos el checkbox, crear uno
                console.log('No se encontró checkbox de DELETE, creando uno temporal');
                const tempCheckbox = document.createElement('input');
                tempCheckbox.type = 'checkbox';
                tempCheckbox.name = 'eliminar_imagen';
                tempCheckbox.value = 'true';
                tempCheckbox.style.display = 'none';
                tempCheckbox.checked = true;
                contenedorImagen.appendChild(tempCheckbox);
                
                // Aplicar estilo visual
                imagen.style.opacity = '0.5';
                overlay.style.display = 'none';
                
                // Añadir indicador visual
                const indicator = document.createElement('div');
                indicator.style.cssText = 'position:absolute; bottom:0; left:0; right:0; background-color:#dc3545; color:white; font-size:12px; text-align:center; padding:2px;';
                indicator.textContent = 'Se eliminará al guardar';
                contenedorImagen.appendChild(indicator);
            }
        });
        
        // Configurar evento de cancelación
        cancelarBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            overlay.style.display = 'none';
        });
    });
    
    // 3. Verificar si ya existen checkboxes de eliminación
    const deleteCheckboxes = document.querySelectorAll('input[id*="DELETE"]');
    console.log('Checkboxes de eliminación encontrados:', deleteCheckboxes.length);
});