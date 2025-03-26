from django.shortcuts import render
from catalogo.models import Producto, Categoria

def inicio(request):
    # Obtener los productos más recientes para mostrar en la página principal
    productos_recientes = Producto.objects.filter(disponible=True).order_by('-id')[:6]
    
    # Obtener todas las categorías para el menú de navegación
    categorias = Categoria.objects.all()
    
    return render(request, 'tienda/inicio.html', {
        'productos_recientes': productos_recientes,
        'categorias': categorias
    })

def acerca(request):
    return render(request, 'tienda/acerca.html')

def contacto(request):
    return render(request, 'tienda/contacto.html')
