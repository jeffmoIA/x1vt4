from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Producto, Categoria, Marca
from .forms import ProductoForm
from .forms import ProductoForm, TallaFormSet
# Función auxiliar para verificar si el usuario es administrador
def es_admin(user):
    return user.is_staff

# === VISTAS DE ADMINISTRACIÓN (CRUD) ===

# Lista de productos (Admin)
@login_required
@user_passes_test(es_admin)
def admin_lista_productos(request):
    productos = Producto.objects.all().order_by('-fecha_creacion')
    return render(request, 'catalogo/admin/lista_productos.html', {
        'productos': productos
    })

# Crear nuevo producto
@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        formset = TallaFormSet(request.POST, prefix='tallas')
        
        if form.is_valid() and formset.is_valid():
            # Guardar el producto
            producto = form.save()
            
            # Guardar las tallas relacionadas
            formset.instance = producto
            formset.save()
            
            messages.success(request, 'Producto creado exitosamente')
            return redirect('catalogo:admin_lista_productos')
    else:
        form = ProductoForm()
        formset = TallaFormSet(prefix='tallas')
    
    return render(request, 'catalogo/admin/editar_producto.html', {
        'form': form,
        'formset': formset,
        'accion': 'Crear'
    })


# Editar producto existente
@login_required
@user_passes_test(es_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        formset = TallaFormSet(request.POST, instance=producto, prefix='tallas')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('catalogo:admin_lista_productos')
    else:
        form = ProductoForm(instance=producto)
        formset = TallaFormSet(instance=producto, prefix='tallas')
    
    return render(request, 'catalogo/admin/editar_producto.html', {
        'form': form,
        'formset': formset,
        'producto': producto,
        'accion': 'Editar'
    })

# Eliminar producto
@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('catalogo:admin_lista_productos')
    
    return render(request, 'catalogo/admin/confirmar_eliminar.html', {
        'producto': producto
    })

def lista_productos(request):
    # Obtener todos los productos disponibles
    productos = Producto.objects.filter(disponible=True)
    
    # Obtener todas las categorías y marcas para los filtros laterales
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    
    # Búsqueda (opcional)
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
    
    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'query': query
    })

def detalle_producto(request, producto_id):
    # Obtener un producto específico por su ID
    producto = get_object_or_404(Producto, id=producto_id, disponible=True)
    
    # Ya no necesitamos filtrar por disponibilidad aquí
    # tallas_disponibles = producto.tallas.filter(disponible=True)
    
    # Obtener productos relacionados (misma categoría, excluyendo el actual)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        disponible=True
    ).exclude(id=producto_id)[:4]  # Limitamos a 4 productos relacionados
    
    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
        # Ya no pasamos tallas_disponibles ya que usaremos producto.tallas.all() en la plantilla
        'productos_relacionados': productos_relacionados
    })

def productos_por_categoria(request, categoria_id):
    # Obtener la categoría o devolver un 404 si no existe
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    # Obtener todos los productos de esa categoría
    productos = Producto.objects.filter(categoria=categoria, disponible=True)
    
    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos,
        'categoria': categoria
    })

def productos_por_marca(request, marca_id):
    # Obtener la marca o devolver un 404 si no existe
    marca = get_object_or_404(Marca, id=marca_id)
    
    # Obtener todos los productos de esa marca
    productos = Producto.objects.filter(marca=marca, disponible=True)
    
    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos,
        'marca': marca
    })