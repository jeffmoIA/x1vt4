/**
 * Solución específica para el botón "Aplicar cambios" que no guarda los cambios
 * Este script se enfoca exclusivamente en resolver este problema
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando solución para el botón Aplicar cambios...');
    
    // Encontrar el formulario principal
    const form = document.querySelector('form');
    if (!form) {
        console.error('No se encontró el formulario principal');
        return;
    }
    
    // Encontrar el botón Aplicar cambios (por ID o texto)
    let btnAplicar = document.getElementById('btn-aplicar-cambios');
    if (!btnAplicar) {
        // Buscar por texto
        document.querySelectorAll('button').forEach(btn => {
            if (btn.textContent.includes('Aplicar') || 
                btn.textContent.includes('aplicar') || 
                btn.textContent.includes('cambios')) {
                btnAplicar = btn;
            }
        });
    }
    
    if (!btnAplicar) {
        console.error('No se encontró el botón Aplicar cambios');
        return;
    }
    
    console.log('Botón encontrado:', btnAplicar);
    
    // Eliminar todos los event listeners existentes
    const nuevoBtn = btnAplicar.cloneNode(true);
    btnAplicar.parentNode.replaceChild(nuevoBtn, btnAplicar);
    btnAplicar = nuevoBtn;
    
    // Configurar evento de click
    btnAplicar.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Click en Aplicar cambios (handler optimizado)');
        
        // Preparar el formulario - Asegurar que todos los formsets estén correctos
        prepararFormulario();
        
        // Mostrar estado de carga
        btnAplicar.disabled = true;
        const textoOriginal = btnAplicar.innerHTML;
        btnAplicar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
        
        // Usar FormData para capturar todos los campos, incluidos archivos
        const formData = new FormData(form);
        formData.append('aplicar_cambios', 'true');
        
        // Log de diagnóstico para ver qué se está enviando
        console.log('Enviando formulario...');
        logFormData(formData);
        
        // Realizar la solicitud AJAX usando Fetch API
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            // No establecer Content-Type, FormData lo hará automáticamente
            // Importante para formularios con archivos
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error de servidor: ${response.status} ${response.statusText}`);
            }
            
            // Intentar parsear como JSON, pero manejar también respuestas no-JSON
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json();
            } else {
                return response.text().then(text => {
                    return { success: true, message: 'Cambios aplicados (respuesta no JSON)' };
                });
            }
        })
        .then(data => {
            // Restaurar el botón
            btnAplicar.disabled = false;
            btnAplicar.innerHTML = textoOriginal;
            
            console.log('Respuesta del servidor:', data);
            
            if (data.success) {
                // Mostrar mensaje de éxito
                mostrarMensaje('success', data.message || 'Cambios aplicados correctamente');
                
                // Actualizar URL si es un producto nuevo
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
                
                // Actualizar la página para reflejar los cambios (opcional)
                // Si prefieres recargar la página para ver los cambios, descomenta la siguiente línea:
                // window.location.reload();
            } else {
                // Mostrar mensaje de error
                mostrarMensaje('error', data.error || 'Error al aplicar los cambios');
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error);
            
            // Restaurar el botón
            btnAplicar.disabled = false;
            btnAplicar.innerHTML = textoOriginal;
            
            // Mostrar mensaje de error
            mostrarMensaje('error', 'Error al procesar la solicitud: ' + error.message);
            
            // Si es un problema grave, podemos intentar un enfoque de respaldo
            const confirmar = confirm(
                'Hubo un problema al guardar los cambios. ' +
                '¿Quieres intentar guardar de forma tradicional?'
            );
            
            if (confirmar) {
                // Crear un campo oculto para indicar que queremos guardar
                const hiddenField = document.createElement('input');
                hiddenField.type = 'hidden';
                hiddenField.name = 'aplicar_cambios';
                hiddenField.value = 'true';
                form.appendChild(hiddenField);
                
                // Enviar el formulario de forma tradicional
                form.submit();
            }
        });
    });
    
    /**
     * Prepara el formulario asegurando que los formsets estén correctamente indexados
     */
    function prepararFormulario() {
        console.log('Preparando formulario...');
        
        // Obtener todos los formsets
        const formsets = [];
        document.querySelectorAll('input[name$="TOTAL_FORMS"]').forEach(input => {
            const name = input.name;
            const prefix = name.replace('-TOTAL_FORMS', '');
            
            formsets.push({
                prefix: prefix,
                totalInput: input,
                container: document.getElementById(`${prefix}-container`) || 
                           document.querySelector(`[id$="${prefix}-container"]`) ||
                           document.querySelector(`[id*="${prefix}"][id*="container"]`)
            });
        });
        
        console.log('Formsets identificados:', formsets);
        
        // Procesar cada formset
        formsets.forEach(formset => {
            if (!formset.container) {
                console.warn(`No se encontró el contenedor para formset ${formset.prefix}`);
                return;
            }
            
            // Buscar elementos de este formset
            const selector = `.${formset.prefix}-form, [class*="${formset.prefix}"]`;
            const elementos = formset.container.querySelectorAll(selector);
            
            console.log(`Formset ${formset.prefix}: ${elementos.length} elementos encontrados`);
            
            // Actualizar contador
            formset.totalInput.value = elementos.length.toString();
            
            // Reindexar elementos
            elementos.forEach((elemento, index) => {
                elemento.querySelectorAll('input, select, textarea').forEach(input => {
                    // Solo procesar si el nombre coincide con el prefijo del formset
                    if (input.name && input.name.startsWith(`${formset.prefix}-`)) {
                        // Extraer el resto del nombre después del índice
                        const match = input.name.match(new RegExp(`^${formset.prefix}-\\d+-(.*)`));
                        if (match) {
                            const fieldName = match[1];
                            const newName = `${formset.prefix}-${index}-${fieldName}`;
                            
                            // Actualizar atributos
                            if (input.name !== newName) {
                                input.name = newName;
                                console.log(`Nombre de campo actualizado: ${newName}`);
                                
                                // Si tiene ID, actualizarlo también
                                if (input.id && input.id.startsWith(`id_${formset.prefix}-`)) {
                                    input.id = `id_${newName}`;
                                }
                            }
                        }
                    }
                });
                
                // Actualizar labels
                elemento.querySelectorAll('label[for^="id_"]').forEach(label => {
                    if (label.htmlFor && label.htmlFor.startsWith(`id_${formset.prefix}-`)) {
                        const match = label.htmlFor.match(new RegExp(`^id_${formset.prefix}-\\d+-(.*)`));
                        if (match) {
                            const fieldName = match[1];
                            label.htmlFor = `id_${formset.prefix}-${index}-${fieldName}`;
                        }
                    }
                });
            });
        });
    }
    
    /**
     * Muestra un mensaje de notificación al usuario
     */
    function mostrarMensaje(tipo, mensaje) {
        console.log(`Mensaje (${tipo}):`, mensaje);
        
        // Intenta usar toastr si está disponible
        if (typeof toastr !== 'undefined') {
            toastr[tipo](mensaje);
            return;
        }
        
        // Intenta usar SweetAlert2 si está disponible
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: tipo === 'error' ? 'error' : 'success',
                title: tipo === 'error' ? 'Error' : 'Éxito',
                text: mensaje
            });
            return;
        }
        
        // Usa alert como último recurso
        if (tipo === 'error') {
            alert('Error: ' + mensaje);
        } else {
            alert(mensaje);
        }
    }
    
    /**
     * Registra el contenido de FormData para diagnóstico
     */
    function logFormData(formData) {
        console.log('Contenido de FormData:');
        for (let pair of formData.entries()) {
            // No mostrar el contenido de los archivos, solo su presencia
            if (pair[1] instanceof File) {
                console.log(pair[0], `[Archivo: ${pair[1].name}, ${pair[1].size} bytes]`);
            } else {
                console.log(pair[0], pair[1]);
            }
        }
    }
});