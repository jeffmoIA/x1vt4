class AdminMenu {
    constructor() {
      this.menuWrapper = document.getElementById('adminMenuWrapper');
      this.menuToggle = document.getElementById('adminMenuToggle');
      this.menuContent = document.getElementById('adminMenuContent');
      this.isOpen = false;
      this.transitionDuration = 300; // ms
      
      if (!this.menuWrapper || !this.menuToggle || !this.menuContent) {
        console.error('Admin menu elements not found in the DOM');
        return;
      }
      
      this.init();
    }
    
    init() {
      // Asignar eventos
      this.menuToggle.addEventListener('click', this.toggleMenu.bind(this));
      document.addEventListener('click', this.handleOutsideClick.bind(this));
      document.addEventListener('keydown', this.handleKeyPress.bind(this));
      window.addEventListener('resize', this.handleResize.bind(this));
      
      // Estado inicial
      this.updateAriaAttributes(false);
      
      console.log('Admin menu initialized successfully');
    }
    
    toggleMenu(event) {
      event && event.preventDefault();
      this.isOpen = !this.isOpen;
      this.updateAriaAttributes(this.isOpen);
      
      if (this.isOpen) {
        this.positionMenu();
      }
    }
    
    updateAriaAttributes(isOpen) {
      this.menuToggle.setAttribute('aria-expanded', isOpen.toString());
      this.menuContent.setAttribute('aria-hidden', (!isOpen).toString());
      
      // Agregar atributos para screen readers
      if (isOpen) {
        this.menuToggle.setAttribute('aria-label', 'Cerrar menú de administración');
      } else {
        this.menuToggle.setAttribute('aria-label', 'Abrir menú de administración');
      }
    }
    
    positionMenu() {
      // Posicionamiento inteligente para evitar problemas en viewport pequeños
      const viewportHeight = window.innerHeight;
      const toggleRect = this.menuToggle.getBoundingClientRect();
      const menuHeight = this.menuContent.offsetHeight;
      
      // Si no hay suficiente espacio debajo, mostrar arriba
      if (toggleRect.bottom + menuHeight > viewportHeight && toggleRect.top > menuHeight) {
        this.menuContent.style.top = 'auto';
        this.menuContent.style.bottom = 'calc(100% + 8px)';
      } else {
        this.menuContent.style.top = 'calc(100% + 8px)';
        this.menuContent.style.bottom = 'auto';
      }
      
      // Ajustar posición horizontal en pantallas pequeñas
      if (window.innerWidth < 768) {
        this.menuContent.style.left = '0';
        this.menuContent.style.right = '0';
        this.menuContent.style.width = '100%';
      } else {
        // Asegurar que el menú no se salga de la pantalla
        const menuWidth = this.menuContent.offsetWidth;
        if (toggleRect.left + menuWidth > window.innerWidth) {
          this.menuContent.style.left = 'auto';
          this.menuContent.style.right = '0';
        } else {
          this.menuContent.style.left = '0';
          this.menuContent.style.right = 'auto';
        }
      }
    }
    
    handleOutsideClick(event) {
      if (this.isOpen && 
          !this.menuWrapper.contains(event.target)) {
        this.toggleMenu();
      }
    }
    
    handleKeyPress(event) {
      // Cerrar con ESC
      if (this.isOpen && event.key === 'Escape') {
        this.toggleMenu();
        this.menuToggle.focus();
      }
      
      // Navegación con teclado dentro del menú
      if (this.isOpen && event.key === 'Tab') {
        const focusableElements = this.menuContent.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // Si se presiona Shift+Tab en el primer elemento, ir al último
        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        } 
        // Si se presiona Tab en el último elemento, ir al primero
        else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
    
    handleResize() {
      if (this.isOpen) {
        this.positionMenu();
      }
    }
    
    // Métodos públicos
    open() {
      if (!this.isOpen) {
        this.toggleMenu();
      }
    }
    
    close() {
      if (this.isOpen) {
        this.toggleMenu();
      }
    }
  }
  
  // Inicializar cuando el DOM esté listo
  document.addEventListener('DOMContentLoaded', () => {
    window.adminMenu = new AdminMenu();
    
    // Diagnóstico avanzado
    console.log('==== DIAGNÓSTICO AVANZADO ====');
    
    // Verificar carga de bibliotecas
    const libraries = {
      'jQuery': typeof jQuery !== 'undefined' ? jQuery.fn.jquery : 'No cargado',
      'Bootstrap': typeof bootstrap !== 'undefined' ? 'Cargado' : 'No cargado',
      'DataTables': typeof jQuery !== 'undefined' && typeof jQuery.fn.DataTable !== 'undefined' ? 'Cargado' : 'No cargado',
      'Toastr': typeof toastr !== 'undefined' ? 'Cargado' : 'No cargado'
    };
    
    console.log('Bibliotecas:');
    Object.entries(libraries).forEach(([name, status]) => {
      console.log(`- ${name}: ${status}`);
    });
    
    // Verificar elementos críticos del DOM
    const criticalElements = [
      'adminMenuWrapper',
      'adminMenuToggle',
      'adminMenuContent'
    ];
    
    console.log('Elementos del DOM:');
    criticalElements.forEach(id => {
      console.log(`- ${id}: ${document.getElementById(id) ? 'Encontrado' : 'No encontrado'}`);
    });

    class DropdownMenu {
        constructor(config) {
          this.wrapper = document.getElementById(config.wrapperId);
          this.toggle = document.getElementById(config.toggleId);
          this.content = document.getElementById(config.contentId);
          this.isOpen = false;
          this.transitionDuration = 300; // ms
          this.name = config.name || 'menú';
          
          if (!this.wrapper || !this.toggle || !this.content) {
            console.error(`Elementos del ${this.name} no encontrados en el DOM`);
            return;
          }
          
          this.init();
        }
        
        init() {
          // Asignar eventos
          this.toggle.addEventListener('click', this.toggleMenu.bind(this));
          document.addEventListener('click', this.handleOutsideClick.bind(this));
          document.addEventListener('keydown', this.handleKeyPress.bind(this));
          window.addEventListener('resize', this.handleResize.bind(this));
          
          // Estado inicial
          this.updateAriaAttributes(false);
          
          console.log(`${this.name} inicializado correctamente`);
        }
        
        toggleMenu(event) {
          event && event.preventDefault();
          this.isOpen = !this.isOpen;
          this.updateAriaAttributes(this.isOpen);
          
          if (this.isOpen) {
            this.positionMenu();
          }
        }
        
        updateAriaAttributes(isOpen) {
          this.toggle.setAttribute('aria-expanded', isOpen.toString());
          this.content.setAttribute('aria-hidden', (!isOpen).toString());
          
          // Agregar atributos para screen readers
          if (isOpen) {
            this.toggle.setAttribute('aria-label', `Cerrar ${this.name}`);
          } else {
            this.toggle.setAttribute('aria-label', `Abrir ${this.name}`);
          }
        }
        
        positionMenu() {
          // Posicionamiento inteligente para evitar problemas en viewport pequeños
          const viewportHeight = window.innerHeight;
          const toggleRect = this.toggle.getBoundingClientRect();
          const menuHeight = this.content.offsetHeight;
          
          // Si no hay suficiente espacio debajo, mostrar arriba
          if (toggleRect.bottom + menuHeight > viewportHeight && toggleRect.top > menuHeight) {
            this.content.style.top = 'auto';
            this.content.style.bottom = 'calc(100% + 8px)';
          } else {
            this.content.style.top = 'calc(100% + 8px)';
            this.content.style.bottom = 'auto';
          }
          
          // Ajustar posición horizontal en pantallas pequeñas
          if (window.innerWidth < 768) {
            this.content.style.left = '0';
            this.content.style.right = '0';
            this.content.style.width = '100%';
          } else {
            // Asegurar que el menú no se salga de la pantalla
            const menuWidth = this.content.offsetWidth;
            if (toggleRect.left + menuWidth > window.innerWidth) {
              this.content.style.left = 'auto';
              this.content.style.right = '0';
            } else {
              this.content.style.left = '0';
              this.content.style.right = 'auto';
            }
          }
        }
        
        handleOutsideClick(event) {
          if (this.isOpen && 
              !this.wrapper.contains(event.target)) {
            this.toggleMenu();
          }
        }
        
        handleKeyPress(event) {
          // Cerrar con ESC
          if (this.isOpen && event.key === 'Escape') {
            this.toggleMenu();
            this.toggle.focus();
          }
          
          // Navegación con teclado dentro del menú
          if (this.isOpen && event.key === 'Tab') {
            const focusableElements = this.content.querySelectorAll('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
            
            if (focusableElements.length === 0) return;
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            // Si se presiona Shift+Tab en el primer elemento, ir al último
            if (event.shiftKey && document.activeElement === firstElement) {
              event.preventDefault();
              lastElement.focus();
            } 
            // Si se presiona Tab en el último elemento, ir al primero
            else if (!event.shiftKey && document.activeElement === lastElement) {
              event.preventDefault();
              firstElement.focus();
            }
          }
        }
        
        handleResize() {
          if (this.isOpen) {
            this.positionMenu();
          }
        }
        
        // Métodos públicos
        open() {
          if (!this.isOpen) {
            this.toggleMenu();
          }
        }
        
        close() {
          if (this.isOpen) {
            this.toggleMenu();
          }
        }
      }
      
      // Script de menú simple y directo
    document.addEventListener('DOMContentLoaded', function() {
        // Función para inicializar un menú desplegable
        function setupMenu(toggleId, menuId) {
            const toggleBtn = document.getElementById(toggleId);
            const menu = document.getElementById(menuId);
            
            if (!toggleBtn || !menu) {
                console.log(`Elementos no encontrados para el menú: ${toggleId} / ${menuId}`);
                return;
            }
            
            console.log(`Configurando menú: ${toggleId}`);
            
            // Función para mostrar/ocultar el menú
            function toggleMenu(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log(`Click en ${toggleId}`);
                
                // Si el menú está visible, ocultarlo; si está oculto, mostrarlo
                if (menu.style.display === 'block') {
                    menu.style.display = 'none';
                    toggleBtn.setAttribute('aria-expanded', 'false');
                } else {
                    menu.style.display = 'block';
                    toggleBtn.setAttribute('aria-expanded', 'true');
                    
                    // Posicionar el menú correctamente
                    positionMenu();
                }
            }
            
            // Función para posicionar el menú
            function positionMenu() {
                const rect = toggleBtn.getBoundingClientRect();
                
                // Posicionar debajo del botón
                menu.style.position = 'absolute';
                menu.style.top = (rect.bottom + window.scrollY) + 'px';
                
                // Alinear a la derecha para menús de usuario/admin en la barra superior
                if (toggleId === 'adminMenuToggle' || toggleId === 'userMenuToggle') {
                    menu.style.right = '0';
                } else {
                    menu.style.left = rect.left + 'px';
                }
                
                // Asegurar que el menú esté visible
                menu.style.zIndex = '1050';
            }
            
            // Cerrar el menú cuando se hace clic fuera de él
            function closeMenuOnOutsideClick(e) {
                if (menu.style.display === 'block' && 
                    !menu.contains(e.target) && 
                    e.target !== toggleBtn && 
                    !toggleBtn.contains(e.target)) {
                    menu.style.display = 'none';
                    toggleBtn.setAttribute('aria-expanded', 'false');
                }
            }
            
            // Cerrar el menú con la tecla Escape
            function closeMenuOnEscape(e) {
                if (e.key === 'Escape' && menu.style.display === 'block') {
                    menu.style.display = 'none';
                    toggleBtn.setAttribute('aria-expanded', 'false');
                }
            }
            
            // Configurar el estado inicial del menú
            menu.style.display = 'none';
            toggleBtn.setAttribute('aria-expanded', 'false');
            
            // Agregar eventos
            toggleBtn.addEventListener('click', toggleMenu);
            document.addEventListener('click', closeMenuOnOutsideClick);
            document.addEventListener('keydown', closeMenuOnEscape);
            
            console.log(`Menú ${toggleId} configurado correctamente`);
        }
        
        // Inicializar menús
        setupMenu('adminMenuToggle', 'adminMenuContent');
        setupMenu('userMenuToggle', 'userMenuContent');
        
        // Diagnóstico
        console.log('DOM cargado, menús inicializados');
    });
  });