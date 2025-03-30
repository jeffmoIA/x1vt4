/**
 * Gestor Avanzado de Imágenes para Productos
 * 
 * Características:
 * - Gestión de imágenes con interfaz moderna
 * - Prevención de errores y gestión robusta de formsets
 * - Sistema de notificaciones integrado
 * - Prevención de conflictos DOM y comportamiento limpio
 */
class ProductImageManager {
    constructor() {
        // Elementos DOM principales
        this.container = document.getElementById('imagenes-container');
        this.totalFormsInput = document.getElementById('id_imagenes-TOTAL_FORMS');
        this.addButton = document.getElementById('add-imagen');
        this.form = document.getElementById('producto-form');
        
        // Estado interno
        this.lastIndex = 0;
        this.formPrefix = 'imagenes';
        
        // Inicialización
        this.init();
    }
    
    init() {
        // Comprobar elementos requeridos
        if (!this.container || !this.totalFormsInput || !this.form) {
            console.error('Elementos DOM requeridos no encontrados');
            return;
        }
        
        // Calcular último índice
        this.calcularUltimoIndice();
        
        // Configurar interfaz inicial
        this.setupImagenes();
        this.setupEventListeners();
        
        console.log('Gestor de imágenes inicializado con éxito');
    }
    
    calcularUltimoIndice() {
        const forms = this.container.querySelectorAll('.imagen-form');
        this.lastIndex = forms.length > 0 ? forms.length - 1 : -1;
        console.log(`Índice inicial calculado: ${this.lastIndex}`);
    }
    
    setupImagenes() {
        // Configurar cada bloque de imagen existente
        const bloques = this.container.querySelectorAll('.imagen-form');
        bloques.forEach(bloque => {
            this.setupImagenExistente(bloque);
        });
        
        // Actualizar contador total
        this.actualizarContadorForms();
    }
    
    setupImagenExistente(bloque) {
        // Asegurar estructura correcta
        this.ensureModernLayout(bloque);
        
        // Configurar checkbox principal
        const checkbox = bloque.querySelector('.principal-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', e => this.handlePrincipalChange(e));
            
            // Si está marcado, aplicar clase especial
            if (checkbox.checked) {
                bloque.classList.add('is-principal');
                this.addPrincipalBadge(bloque);
            }
        }
        
        // Configurar botón eliminar
        const deleteBtn = bloque.querySelector('.btn-eliminar-imagen');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', e => this.handleEliminar(e));
        } else {
            this.addDeleteButton(bloque);
        }
    }
    
    ensureModernLayout(bloque) {
        // Verificar si ya tiene la estructura moderna
        if (bloque.querySelector('.image-preview')) {
            return; // Ya tiene estructura moderna
        }
        
        // Reorganizar estructura al formato moderno
        const imageContainer = bloque.querySelector('.image-container');
        const imageInput = bloque.querySelector('input[type="file"]');
        const ordenInput = bloque.querySelector('input[name*="-orden"]');
        const principalCheck = bloque.querySelector('input[name*="-es_principal"]');
        const tituloInput = bloque.querySelector('input[name*="-titulo"]');
        
        // Crear contenedor de vista previa
        const previewDiv = document.createElement('div');
        previewDiv.className = 'image-preview';
        
        // Mover imagen si existe
        if (imageContainer && imageContainer.querySelector('img')) {
            const img = imageContainer.querySelector('img').cloneNode(true);
            previewDiv.appendChild(img);
            imageContainer.remove();
        }
        
        // Limpiar bloque y reconstruir
        bloque.innerHTML = '';
        bloque.appendChild(previewDiv);
        
        // Reconstruir formulario
        const formElements = document.createElement('div');
        formElements.className = 'form-elements';
        
        // Recrear input de imagen
        const imageGroup = document.createElement('div');
        imageGroup.className = 'form-group';
        const imageLabel = document.createElement('label');
        imageLabel.className = 'form-label';
        imageLabel.textContent = 'Imagen';
        imageGroup.appendChild(imageLabel);
        
        if (imageInput) {
            imageGroup.appendChild(imageInput);
        }
        
        formElements.appendChild(imageGroup);
        
        // Recrear input de orden
        if (ordenInput) {
            const ordenGroup = document.createElement('div');
            ordenGroup.className = 'form-group';
            const ordenLabel = document.createElement('label');
            ordenLabel.className = 'form-label';
            ordenLabel.textContent = 'Orden';
            ordenGroup.appendChild(ordenLabel);
            ordenGroup.appendChild(ordenInput);
            formElements.appendChild(ordenGroup);
        }
        
        // Recrear checkbox principal
        if (principalCheck) {
            const principalGroup = document.createElement('div');
            principalGroup.className = 'principal-group';
            principalGroup.appendChild(principalCheck);
            const principalLabel = document.createElement('label');
            principalLabel.textContent = 'Es imagen principal';
            principalGroup.appendChild(principalLabel);
            formElements.appendChild(principalGroup);
        }
        
        // Recrear input de título
        if (tituloInput) {
            const tituloGroup = document.createElement('div');
            tituloGroup.className = 'form-group';
            const tituloLabel = document.createElement('label');
            tituloLabel.className = 'form-label';
            tituloLabel.textContent = 'Título (opcional)';
            tituloGroup.appendChild(tituloLabel);
            tituloGroup.appendChild(tituloInput);
            formElements.appendChild(tituloGroup);
        }
        
        // Añadir elementos al bloque
        bloque.appendChild(formElements);
        
        // Añadir botones de acción
        this.addDeleteButton(bloque);
    }
    
    addDeleteButton(bloque) {
        // Verificar si ya tiene botón de eliminar
        if (bloque.querySelector('.btn-eliminar-imagen')) {
            return;
        }
        
        // Crear contenedor de acciones
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'imagen-actions';
        
        // Crear botón eliminar
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'btn btn-danger btn-eliminar-imagen';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Eliminar imagen';
        deleteBtn.addEventListener('click', e => this.handleEliminar(e));
        
        // Añadir al contenedor
        actionsDiv.appendChild(deleteBtn);
        bloque.appendChild(actionsDiv);
    }
    
    addPrincipalBadge(bloque) {
        // Verificar si ya tiene badge
        if (bloque.querySelector('.principal-badge')) {
            return;
        }
        
        // Crear badge
        const badge = document.createElement('div');
        badge.className = 'principal-badge';
        badge.textContent = 'Principal';
        
        // Añadir al bloque
        bloque.appendChild(badge);
    }
    
    removePrincipalBadge(bloque) {
        const badge = bloque.querySelector('.principal-badge');
        if (badge) {
            badge.remove();
        }
    }
    
    setupEventListeners() {
        // Botón para añadir nueva imagen
        if (this.addButton) {
            this.addButton.addEventListener('click', () => this.addNewImage());
        }
        
        // Validación antes de enviar formulario
        if (this.form) {
            this.form.addEventListener('submit', e => this.handleFormSubmit(e));
        }
        
        // Botones de acción
        const applyBtn = document.getElementById('btn-aplicar-cambios');
        const saveBtn = document.getElementById('btn-guardar-salir');
        
        if (applyBtn) {
            applyBtn.addEventListener('click', e => this.handleApplyChanges(e));
        }
        
        if (saveBtn) {
            saveBtn.addEventListener('click', e => this.handleSaveExit(e));
        }
    }
    
    handleFormSubmit(e) {
        // Actualizar formularios antes de enviar
        this.actualizarIndicesFormularios();
    }
    
    handleApplyChanges(e) {
        e.preventDefault();
        
        // Actualizar formularios
        this.actualizarIndicesFormularios();
        
        // Preparar datos
        const formData = new FormData(this.form);
        formData.append('aplicar_cambios', 'true');
        
        // Mostrar carga
        const btn = e.target;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Aplicando...';
        
        // Enviar solicitud
        fetch(this.form.action, {
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
            return response.json();
        })
        .then(data => {
            // Restaurar botón
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Aplicar cambios';
            
            if (data.success) {
                // Mostrar éxito
                this.mostrarNotificacion('success', data.message || 'Cambios aplicados correctamente');
                
                // Actualizar URL si es nuevo
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
                
                // Aplicar cambios localmente (reconstruir interfaz)
                this.refreshAfterSave();
            } else {
                // Mostrar error
                this.mostrarNotificacion('error', data.error || 'Error al aplicar cambios');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Restaurar botón
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Aplicar cambios';
            
            // Mostrar error
            this.mostrarNotificacion('error', 'Error de conexión: ' + error.message);
        });
    }
    
    handleSaveExit(e) {
        e.preventDefault();
        
        // Actualizar formularios
        this.actualizarIndicesFormularios();
        
        // Añadir campo para redirección
        const inputRedirigir = document.createElement('input');
        inputRedirigir.type = 'hidden';
        inputRedirigir.name = 'redirigir';
        inputRedirigir.value = 'true';
        this.form.appendChild(inputRedirigir);
        
        // Mostrar carga
        const btn = e.target;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
        
        // Enviar formulario
        this.form.submit();
    }
    
    handlePrincipalChange(e) {
        const checkbox = e.target;
        const bloque = checkbox.closest('.imagen-form');
        
        if (checkbox.checked) {
            // Desmarcar otros
            this.container.querySelectorAll('.principal-checkbox').forEach(cb => {
                if (cb !== checkbox) {
                    cb.checked = false;
                    const otherBloque = cb.closest('.imagen-form');
                    if (otherBloque) {
                        otherBloque.classList.remove('is-principal');
                        this.removePrincipalBadge(otherBloque);
                    }
                }
            });
            
            // Marcar este como principal
            bloque.classList.add('is-principal');
            this.addPrincipalBadge(bloque);
        } else {
            // Quitar marca principal
            bloque.classList.remove('is-principal');
            this.removePrincipalBadge(bloque);
        }
    }
    
    handleEliminar(e) {
        const btn = e.target.closest('.btn-eliminar-imagen');
        if (!btn) return;
        
        const bloque = btn.closest('.imagen-form');
        if (!bloque) return;
        
        if (confirm('¿Estás seguro de eliminar esta imagen?')) {
            // Buscar checkbox DELETE
            const deleteCheck = bloque.querySelector('input[name$="-DELETE"]');
            
            if (deleteCheck) {
                // Es una imagen existente, marcar para eliminar
                deleteCheck.checked = true;
                bloque.classList.add('marked-for-deletion');
                
                // Cambiar texto del botón
                btn.className = 'btn btn-warning btn-eliminar-imagen';
                btn.innerHTML = '<i class="fas fa-undo"></i> Restaurar';
                
                // Cambiar comportamiento
                btn.removeEventListener('click', this.handleEliminar);
                btn.addEventListener('click', e => this.handleRestaurar(e));
            } else {
                // Es una imagen nueva, eliminar del DOM
                bloque.remove();
                this.actualizarContadorForms();
            }
        }
    }
    
    handleRestaurar(e) {
        const btn = e.target.closest('.btn-eliminar-imagen');
        if (!btn) return;
        
        const bloque = btn.closest('.imagen-form');
        if (!bloque) return;
        
        // Buscar checkbox DELETE
        const deleteCheck = bloque.querySelector('input[name$="-DELETE"]');
        if (deleteCheck) {
            // Desmarcar para no eliminar
            deleteCheck.checked = false;
            bloque.classList.remove('marked-for-deletion');
            
            // Restaurar botón
            btn.className = 'btn btn-danger btn-eliminar-imagen';
            btn.innerHTML = '<i class="fas fa-trash"></i> Eliminar imagen';
            
            // Restaurar comportamiento
            btn.removeEventListener('click', this.handleRestaurar);
            btn.addEventListener('click', e => this.handleEliminar(e));
        }
    }
    
    addNewImage() {
        // Incrementar índice
        this.lastIndex++;
        const newIndex = this.lastIndex;
        
        // Crear nuevo bloque
        const nuevoBloque = document.createElement('div');
        nuevoBloque.className = 'imagen-form';
        
        // Estructura HTML para el nuevo bloque
        nuevoBloque.innerHTML = `
            <div class="image-preview"></div>
            <div class="form-elements">
                <div class="form-group">
                    <label class="form-label">Imagen</label>
                    <input type="file" name="${this.formPrefix}-${newIndex}-imagen" 
                           id="id_${this.formPrefix}-${newIndex}-imagen" 
                           class="form-control" accept="image/*">
                </div>
                <div class="form-group">
                    <label class="form-label">Orden</label>
                    <input type="number" name="${this.formPrefix}-${newIndex}-orden" 
                           id="id_${this.formPrefix}-${newIndex}-orden" 
                           value="${newIndex}" min="0" class="form-control">
                </div>
                <div class="principal-group">
                    <input type="checkbox" name="${this.formPrefix}-${newIndex}-es_principal" 
                           id="id_${this.formPrefix}-${newIndex}-es_principal" 
                           class="principal-checkbox">
                    <label for="id_${this.formPrefix}-${newIndex}-es_principal">Es imagen principal</label>
                </div>
                <div class="form-group">
                    <label class="form-label">Título (opcional)</label>
                    <input type="text" name="${this.formPrefix}-${newIndex}-titulo" 
                           id="id_${this.formPrefix}-${newIndex}-titulo" 
                           class="form-control" placeholder="Descripción de la imagen">
                </div>
            </div>
        `;
        
        // Añadir botón eliminar
        this.addDeleteButton(nuevoBloque);
        
        // Añadir gestión de principal
        const principalCheck = nuevoBloque.querySelector('.principal-checkbox');
        if (principalCheck) {
            principalCheck.addEventListener('change', e => this.handlePrincipalChange(e));
        }
        
        // Añadir al contenedor
        this.container.appendChild(nuevoBloque);
        
        // Actualizar contador
        this.actualizarContadorForms();
        
        // Configurar vista previa
        const fileInput = nuevoBloque.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', e => this.handleFileChange(e));
        }
    }
    
    handleFileChange(e) {
        const input = e.target;
        const previewDiv = input.closest('.imagen-form').querySelector('.image-preview');
        
        if (input.files && input.files[0] && previewDiv) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                // Limpiar vista previa
                previewDiv.innerHTML = '';
                
                // Crear nueva imagen
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = 'Vista previa';
                
                // Añadir a la vista previa
                previewDiv.appendChild(img);
            };
            
            reader.readAsDataURL(input.files[0]);
        }
    }
    
    actualizarContadorForms() {
        if (!this.totalFormsInput) return;
        
        const forms = this.container.querySelectorAll('.imagen-form');
        this.totalFormsInput.value = forms.length;
        console.log(`Total de formularios actualizado: ${forms.length}`);
    }
    
    actualizarIndicesFormularios() {
        if (!this.container || !this.totalFormsInput) return;
        
        // Obtener todos los bloques visibles
        const bloques = Array.from(this.container.querySelectorAll('.imagen-form'));
        
        // Actualizar contador
        this.totalFormsInput.value = bloques.length;
        
        // Re-indexar para asegurar secuencia correcta
        bloques.forEach((bloque, index) => {
            // Actualizar inputs
            bloque.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name && input.name.match(new RegExp(`^${this.formPrefix}-\\d+-`))) {
                    const newName = input.name.replace(
                        new RegExp(`^${this.formPrefix}-\\d+-`), 
                        `${this.formPrefix}-${index}-`
                    );
                    input.name = newName;
                }
                
                if (input.id && input.id.match(new RegExp(`^id_${this.formPrefix}-\\d+-`))) {
                    const newId = input.id.replace(
                        new RegExp(`^id_${this.formPrefix}-\\d+-`), 
                        `id_${this.formPrefix}-${index}-`
                    );
                    input.id = newId;
                }
            });
            
            // Actualizar labels
            bloque.querySelectorAll('label').forEach(label => {
                if (label.htmlFor && label.htmlFor.match(new RegExp(`^id_${this.formPrefix}-\\d+-`))) {
                    const newFor = label.htmlFor.replace