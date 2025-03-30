/**
 * Solución directa para los botones de acción
 * Este script solo se enfoca en hacer que los botones funcionen
 * e ignora completamente cualquier error no relacionado
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando fix para botones...');
    
    // Obtener el formulario
    const form = document.querySelector('form');
    if (!form) {
        console.error('No se encontró el formulario');
        return;
    }
    
    // Encontrar y configurar los botones por texto
    document.querySelectorAll('button').forEach(function(btn) {
        const text = btn.textContent.trim().toLowerCase();
        
        // Botón Aplicar cambios
        if (text.includes('aplicar') || text.includes('cambios')) {
            console.log('Configurando botón Aplicar cambios:', btn);
            configureAplicarButton(btn, form);
        }
        // Botón Guardar y salir
        else if (text.includes('guardar') || text.includes('salir')) {
            console.log('Configurando botón Guardar y salir:', btn);
            configureGuardarButton(btn, form);
        }
    });
    
    /**
     * Configura el botón Aplicar cambios
     */
    function configureAplicarButton(btn, form) {
        // Eliminar todos los event listeners existentes
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        // Añadir nuevo event listener
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Click en botón Aplicar cambios');
            
            // Preparar datos
            const formData = new FormData(form);
            formData.append('aplicar_cambios', 'true');
            
            // Mostrar indicador de carga
            this.disabled = true;
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Aplicando...';
            
            // Enviar solicitud
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(function(data) {
                // Restaurar botón
                newBtn.disabled = false;
                newBtn.innerHTML = originalText;
                
                // Mostrar mensaje
                if (data.success) {
                    alert('Cambios aplicados correctamente');
                    // Recargar la página para ver los cambios
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Error al aplicar cambios'));
                }
            })
            .catch(function(error) {
                console.error('Error:', error);
                // Restaurar botón
                newBtn.disabled = false;
                newBtn.innerHTML = originalText;
                alert('Error: ' + error.message);
            });
        });
    }
    
    /**
     * Configura el botón Guardar y salir
     */
    function configureGuardarButton(btn, form) {
        // Eliminar todos los event listeners existentes
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        // Añadir nuevo event listener
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Click en botón Guardar y salir');
            
            // Añadir campo de redirección
            let input = form.querySelector('input[name="redirigir"]');
            if (!input) {
                input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'redirigir';
                form.appendChild(input);
            }
            input.value = 'true';
            
            // Mostrar indicador de carga
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
            
            // Enviar formulario después de un pequeño retraso
            setTimeout(function() {
                form.submit();
            }, 100);
        });
    }
});