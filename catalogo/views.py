from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Producto, Categoria, Marca
from .forms import ProductoForm
from .forms import ProductoForm, TallaFormSet
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from django.urls import reverse

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
    # Usamos select_related para precargar categoría y marca en una sola consulta
    productos = Producto.objects.filter(disponible=True).select_related('categoria', 'marca')
    
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
    # Usamos select_related para cargar categoría y marca en una sola consulta
    producto = get_object_or_404(
        Producto.objects.select_related('categoria', 'marca'),
        id=producto_id, 
        disponible=True
    )
    
    # Obtener productos relacionados (misma categoría, excluyendo el actual)
    # También usamos select_related para los productos relacionados
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        disponible=True
    ).exclude(id=producto_id).select_related('categoria', 'marca')[:4]
    
    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
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
    
@login_required
@user_passes_test(es_admin)
def admin_productos_data(request):
    """
    Vista para procesar solicitudes AJAX de DataTables y devolver datos de productos paginados
    """
    # Obtener los parámetros enviados por DataTables
    draw = int(request.POST.get('draw', 1))  # Contador de solicitudes
    start = int(request.POST.get('start', 0))  # Inicio de la paginación
    length = int(request.POST.get('length', 10))  # Cantidad de registros a mostrar
    search_value = request.POST.get('search[value]', '')  # Valor de búsqueda
    
    # Obtener columna de ordenamiento y dirección
    order_column_index = request.POST.get('order[0][column]', 1)  # Índice de la columna a ordenar
    order_column = request.POST.get(f'columns[{order_column_index}][data]', 'nombre')  # Nombre de la columna
    order_dir = request.POST.get('order[0][dir]', 'asc')  # Dirección de ordenamiento
    
    # Convertir el índice de columna a un nombre de campo real
    column_mapping = {
        '0': 'id',
        '1': 'nombre',
        '2': 'precio',
        '3': 'categoria__nombre',
        '4': 'marca__nombre',
        '5': 'stock',
        '6': 'disponible'
    }
    order_column = column_mapping.get(order_column_index, 'nombre')
    
    # Preparar el ordenamiento
    if order_dir == 'desc':
        order_column = f'-{order_column}'  # Agregar un signo menos para ordenar descendentemente
    
    # Preparar la consulta base
    queryset = Producto.objects.all()
    
    # Filtrar por término de búsqueda si existe
    if search_value:
        queryset = queryset.filter(
            Q(nombre__icontains=search_value) |
            Q(descripcion__icontains=search_value) |
            Q(categoria__nombre__icontains=search_value) |
            Q(marca__nombre__icontains=search_value)
        )
    
    # Total de registros (sin filtrar)
    total_records = Producto.objects.count()
    # Total de registros (después de filtrar)
    total_records_filtered = queryset.count()
    
    # Ordenar y paginar los resultados
    queryset = queryset.order_by(order_column)[start:start + length]
    
    # Preparar los datos para la respuesta
    data = []
    for producto in queryset:
        # URL de la imagen (o placeholder si no hay imagen)
        imagen_url = producto.imagen.url if producto.imagen else '/static/img/placeholder.png'
        
        # Estado de disponibilidad formateado como HTML
        if producto.disponible:
            disponible_html = '<span class="badge bg-success">Sí</span>'
        else:
            disponible_html = '<span class="badge bg-danger">No</span>'
        
        # URL de las acciones
        editar_url = reverse('catalogo:editar_producto', args=[producto.id])
        eliminar_url = reverse('catalogo:eliminar_producto', args=[producto.id])
        
        # Botones de acción
        acciones_html = f'''
        <div class="btn-group" role="group">
            <a href="{editar_url}" class="btn btn-sm btn-warning">
                <i class="fas fa-edit"></i>
            </a>
            <a href="{eliminar_url}" class="btn btn-sm btn-danger">
                <i class="fas fa-trash"></i>
            </a>
        </div>
        '''
        
        # Agregar el producto a la lista de datos
        data.append({
            'imagen': f'<img src="{imagen_url}" alt="{producto.nombre}" width="50">',
            'nombre': producto.nombre,
            'precio': f'${producto.precio}',
            'categoria': producto.categoria.nombre,
            'marca': producto.marca.nombre,
            'stock': producto.stock,
            'disponible': disponible_html,
            'acciones': acciones_html
        })
    
    # Preparar la respuesta JSON según el formato esperado por DataTables
    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_records_filtered,
        'data': data
    }
    
    return JsonResponse(response)