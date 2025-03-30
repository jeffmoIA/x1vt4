document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando menús desplegables personalizados...');
    
    // Función para configurar un menú desplegable
    function setupDropdown(toggleId, menuId) {
        const toggle = document.getElementById(toggleId);
        const menu = document.getElementById(menuId);
        
        if (!toggle || !menu) {
            console.error(`No se encontraron elementos para el menú ${toggleId}`);
            return;
        }
        
        // Función para alternar la visibilidad del menú
        function toggleMenu(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Si está visible, ocultar; si está oculto, mostrar
            const isVisible = menu.style.display === 'block';
            menu.style.display = isVisible ? 'none' : 'block';
            
            // Registrar acción en consola
            console.log(`${toggleId}: Menú ${isVisible ? 'cerrado' : 'abierto'}`);
        }
        
        // Cerrar cuando se hace clic fuera
        function closeOnOutsideClick(e) {
            if (menu.style.display === 'block' && 
                !menu.contains(e.target) && 
                e.target !== toggle && 
                !toggle.contains(e.target)) {
                menu.style.display = 'none';
            }
        }
        
        // Cerrar cuando se presiona la tecla Escape
        function closeOnEscape(e) {
            if (e.key === 'Escape' && menu.style.display === 'block') {
                menu.style.display = 'none';
            }
        }
        
        // Eliminar posibles listeners antiguos
        const newToggle = toggle.cloneNode(true);
        toggle.parentNode.replaceChild(newToggle, toggle);
        
        // Agregar event listeners
        newToggle.addEventListener('click', toggleMenu);
        document.addEventListener('click', closeOnOutsideClick);
        document.addEventListener('keydown', closeOnEscape);
        
        console.log(`Menú ${toggleId} configurado correctamente`);
    }
    
    // Configurar todos los menús desplegables
    setupDropdown('adminDropdownToggle', 'adminDropdownMenu');
    setupDropdown('userDropdownToggle', 'userDropdownMenu');
    
    // Registrar diagnóstico
    console.log('=== DIAGNÓSTICO DE MENÚS ===');
    console.log('adminDropdownToggle:', document.getElementById('adminDropdownToggle') ? 'Encontrado' : 'No encontrado');
    console.log('adminDropdownMenu:', document.getElementById('adminDropdownMenu') ? 'Encontrado' : 'No encontrado');
    console.log('userDropdownToggle:', document.getElementById('userDropdownToggle') ? 'Encontrado' : 'No encontrado'); 
    console.log('userDropdownMenu:', document.getElementById('userDropdownMenu') ? 'Encontrado' : 'No encontrado');
});