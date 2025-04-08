/**
 * Script para añadir funcionalidad de búsqueda al modal de marcas
 * Este archivo se ejecuta de forma independiente y evita conflictos
 */
(function() {
    // Esperar a que el DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', function() {
      // Referencia al botón que abre el modal
      const btnAbrirModal = document.getElementById('btnGestionarMarcas');
      
      if (btnAbrirModal) {
        btnAbrirModal.addEventListener('click', function() {
          // Dar tiempo a que el modal se abra completamente
          setTimeout(mejorarInterfazMarcas, 500);
        });
      }
    });
    
    // Función principal para mejorar la interfaz
    function mejorarInterfazMarcas() {
      // Referencias a elementos del modal
      const modal = document.getElementById('gestionMarcasModal');
      const listaMarcas = document.getElementById('listaMarcasExistentes');
      
      if (!modal || !listaMarcas) return;
      
      // Añadir campo de búsqueda si no existe
      if (!document.getElementById('buscadorMarcasRapido')) {
        const divBuscador = document.createElement('div');
        divBuscador.className = 'input-group mb-3';
        divBuscador.innerHTML = `
          <span class="input-group-text bg-light">
            <i class="fas fa-search"></i>
          </span>
          <input type="text" id="buscadorMarcasRapido" class="form-control" 
                 placeholder="Filtrar marcas..." autocomplete="off">
        `;
        
        // Insertar antes de la lista de marcas
        listaMarcas.parentNode.insertBefore(divBuscador, listaMarcas);
        
        // Configurar el buscador
        const inputBuscador = document.getElementById('buscadorMarcasRapido');
        if (inputBuscador) {
          inputBuscador.addEventListener('input', filtrarMarcas);
        }
      }
    }
    
    // Función para filtrar marcas
    function filtrarMarcas() {
      const termino = this.value.toLowerCase().trim();
      const listaMarcas = document.getElementById('listaMarcasExistentes');
      const elementos = listaMarcas.querySelectorAll('.list-group-item');
      
      let hayResultados = false;
      
      // Filtrar cada elemento
      elementos.forEach(function(item) {
        const textoMarca = item.textContent.trim().toLowerCase();
        
        if (textoMarca.includes(termino)) {
          item.style.display = '';
          hayResultados = true;
        } else {
          item.style.display = 'none';
        }
      });
      
      // Mostrar mensaje si no hay resultados
      let mensajeNoResultados = listaMarcas.querySelector('.sin-resultados');
      
      if (!hayResultados) {
        if (!mensajeNoResultados) {
          mensajeNoResultados = document.createElement('div');
          mensajeNoResultados.className = 'alert alert-info text-center sin-resultados';
          mensajeNoResultados.textContent = 'No se encontraron marcas con ese filtro';
          listaMarcas.appendChild(mensajeNoResultados);
        }
      } else if (mensajeNoResultados) {
        mensajeNoResultados.remove();
      }
    }
  })();