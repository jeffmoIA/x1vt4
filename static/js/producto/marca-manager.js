// Script simple para gestionar marcas sin dependencias externas
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos
    const btnGestionar = document.getElementById('btn-gestionar-marca');
    const marcasPanel = document.getElementById('marcasPanel');
    const formNuevaMarca = document.getElementById('formNuevaMarca');
    const inputNuevaMarca = document.getElementById('nuevaMarcaNombre');
    const btnGuardarMarca = document.getElementById('btnGuardarMarca');
    const listaMarcas = document.getElementById('listaMarcas');
    const selectorMarca = document.getElementById('id_marca');
    const buscarMarca = document.getElementById('buscarMarca');
    const marcaMessage = document.getElementById('marcaMessage');
    
    // URLs para operaciones AJAX
    const urlListar = document.getElementById('url-listar-marcas')?.value || '';
    const urlCrear = document.getElementById('url-crear-marca')?.value || '';
    const urlEliminar = document.getElementById('url-eliminar-marca')?.value || '';
    
    // Obtener token CSRF
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    
    // Función para mostrar/ocultar panel
    function togglePanel() {
        if (marcasPanel.style.display === 'none') {
            marcasPanel.style.display = 'block';
            cargarMarcas();
        } else {
            marcasPanel.style.display = 'none';
        }
    }
    
    // Cargar marcas
    function cargarMarcas() {
        if (!urlListar) {
            mostrarMensaje('Error: URL para listar marcas no configurada', 'danger');
            return;
        }
        
        listaMarcas.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span class="ms-2">Cargando marcas...</span>
            </div>
        `;
        
        fetch(urlListar)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderizarMarcas(data.marcas);
                } else {
                    mostrarMensaje(data.error || 'Error al cargar marcas', 'danger');
                    listaMarcas.innerHTML = '<div class="alert alert-danger">Error al cargar marcas</div>';
                }
            })
            .catch(error => {
                console.error('Error al cargar marcas:', error);
                listaMarcas.innerHTML = '<div class="alert alert-danger">Error de conexión</div>';
            });
    }
    
    // Renderizar lista de marcas
    function renderizarMarcas(marcas) {
        if (!marcas || marcas.length === 0) {
            listaMarcas.innerHTML = '<div class="alert alert-info">No hay marcas disponibles</div>';
            return;
        }
        
        let html = '<ul class="list-group list-group-flush">';
        
        marcas.forEach(marca => {
            const puedeEliminar = marca.productos_count === 0;
            
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center marca-item" 
                    data-id="${marca.id}" data-nombre="${marca.nombre}">
                    <div>
                        <span class="marca-nombre">${marca.nombre}</span>
                        <small class="text-muted d-block">${marca.productos_count} productos</small>
                    </div>
                    <div>
                        <button type="button" class="btn btn-sm btn-primary btn-usar-marca">
                            Usar
                        </button>
                        ${puedeEliminar ? `
                            <button type="button" class="btn btn-sm btn-danger btn-eliminar-marca ms-1">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                    </div>
                </li>
            `;
        });
        
        html += '</ul>';
        listaMarcas.innerHTML = html;
        
        // Añadir eventos a los botones
        document.querySelectorAll('.btn-usar-marca').forEach(btn => {
            btn.addEventListener('click', function() {
                const li = this.closest('.marca-item');
                const id = li.dataset.id;
                const nombre = li.dataset.nombre;
                
                // Seleccionar en el select
                if (selectorMarca) {
                    selectorMarca.value = id;
                }
                
                mostrarMensaje(`Marca "${nombre}" seleccionada`, 'success');
                marcasPanel.style.display = 'none';
            });
        });
        
        document.querySelectorAll('.btn-eliminar-marca').forEach(btn => {
            btn.addEventListener('click', function() {
                const li = this.closest('.marca-item');
                const id = li.dataset.id;
                const nombre = li.dataset.nombre;
                
                if (confirm(`¿Estás seguro de eliminar la marca "${nombre}"?`)) {
                    eliminarMarca(id, nombre, li);
                }
            });
        });
    }
    
    // Crear marca
    function crearMarca(nombre) {
        if (!nombre) {
            mostrarMensaje('El nombre de la marca es requerido', 'danger');
            return;
        }
        
        // Mostrar cargando
        btnGuardarMarca.disabled = true;
        btnGuardarMarca.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        
        // Preparar datos
        const formData = new FormData();
        formData.append('nombre', nombre);
        formData.append('csrfmiddlewaretoken', csrftoken);
        
        // Enviar solicitud
        fetch(urlCrear, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpiar input
                inputNuevaMarca.value = '';
                
                // Mostrar mensaje
                mostrarMensaje(`Marca "${data.nombre}" ${data.existed ? 'seleccionada' : 'creada'} correctamente`, 'success');
                
                // Añadir al select si no existe
                if (!document.querySelector(`#id_marca option[value="${data.id}"]`)) {
                    const option = document.createElement('option');
                    option.value = data.id;
                    option.text = data.nombre;
                    selectorMarca.appendChild(option);
                }
                
                // Seleccionar en el select
                selectorMarca.value = data.id;
                
                // Recargar lista
                cargarMarcas();
            } else {
                mostrarMensaje(data.error || 'Error al crear la marca', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error de conexión', 'danger');
        })
        .finally(() => {
            // Restaurar botón
            btnGuardarMarca.disabled = false;
            btnGuardarMarca.innerHTML = '<i class="fas fa-save"></i> Guardar';
        });
    }
    
    // Eliminar marca
    function eliminarMarca(id, nombre, elemento) {
        if (!id) return;
        
        // Mostrar cargando
        elemento.classList.add('opacity-50');
        const btnEliminar = elemento.querySelector('.btn-eliminar-marca');
        if (btnEliminar) {
            btnEliminar.disabled = true;
            btnEliminar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        }
        
        // Preparar datos
        const formData = new FormData();
        formData.append('id', id);
        formData.append('csrfmiddlewaretoken', csrftoken);
        
        // Enviar solicitud
        fetch(urlEliminar, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Eliminar del DOM con animación
                elemento.style.height = elemento.offsetHeight + 'px';
                elemento.style.transition = 'all 0.3s';
                elemento.style.overflow = 'hidden';
                
                setTimeout(() => {
                    elemento.style.height = '0';
                    elemento.style.padding = '0';
                    elemento.style.margin = '0';
                    
                    setTimeout(() => {
                        elemento.remove();
                        
                        // Eliminar del select
                        const option = selectorMarca.querySelector(`option[value="${id}"]`);
                        if (option) {
                            option.remove();
                        }
                        
                        mostrarMensaje(`Marca "${nombre}" eliminada correctamente`, 'success');
                    }, 300);
                }, 10);
            } else {
                mostrarMensaje(data.error || 'Error al eliminar la marca', 'danger');
                
                // Restaurar elemento
                elemento.classList.remove('opacity-50');
                if (btnEliminar) {
                    btnEliminar.disabled = false;
                    btnEliminar.innerHTML = '<i class="fas fa-trash"></i>';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error de conexión', 'danger');
            
            // Restaurar elemento
            elemento.classList.remove('opacity-50');
            if (btnEliminar) {
                btnEliminar.disabled = false;
                btnEliminar.innerHTML = '<i class="fas fa-trash"></i>';
            }
        });
    }
    
    // Filtrar marcas
    function filtrarMarcas(texto) {
        const items = document.querySelectorAll('.marca-item');
        const busqueda = texto.toLowerCase();
        
        items.forEach(item => {
            const nombre = item.querySelector('.marca-nombre').textContent.toLowerCase();
            if (nombre.includes(busqueda)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    // Mostrar mensaje
    function mostrarMensaje(mensaje, tipo) {
        marcaMessage.textContent = mensaje;
        marcaMessage.className = 'form-text mt-1';
        
        if (tipo === 'success') {
            marcaMessage.classList.add('text-success');
        } else if (tipo === 'danger') {
            marcaMessage.classList.add('text-danger');
        } else if (tipo === 'warning') {
            marcaMessage.classList.add('text-warning');
        }
        
        // Auto-ocultar mensajes de éxito
        if (tipo === 'success') {
            setTimeout(() => {
                marcaMessage.style.opacity = '0';
                marcaMessage.style.transition = 'opacity 0.5s';
                
                setTimeout(() => {
                    marcaMessage.textContent = '';
                    marcaMessage.style.opacity = '1';
                }, 500);
            }, 3000);
        }
    }
    
    // Configurar eventos
    if (btnGestionar) {
        btnGestionar.addEventListener('click', togglePanel);
    }
    
    if (formNuevaMarca) {
        formNuevaMarca.addEventListener('submit', function(e) {
            e.preventDefault();
            crearMarca(inputNuevaMarca.value.trim());
        });
    }
    
    if (buscarMarca) {
        buscarMarca.addEventListener('input', function() {
            filtrarMarcas(this.value);
        });
    }
});