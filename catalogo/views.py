from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.urls import reverse
from .models import Producto, Categoria, Marca, ImagenProducto
from .forms import ProductoForm, TallaFormSet, ImagenFormSet
from .filters import ProductoFilter
import time

# Función auxiliar para verificar si el usuario es administrador
def es_admin(user):
    return user.is_staff

# === VISTAS DE ADMINISTRACIÓN (CRUD) ===

# Lista de productos (Admin)
@login_required
@user_passes_test(es_admin)
def admin_lista_productos(request):
    """
    Vista para que los administradores gestionen productos con filtros
    por categoría y marca.
    """
    # Obtener listas para los filtros
    categorias = Categoria.objects.all().order_by('nombre')
    marcas = Marca.objects.all().order_by('nombre')
    
    return render(request, 'catalogo/admin/lista_productos.html', {
        'categorias': categorias,
        'marcas': marcas
    })

# Crear nuevo producto
@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    """
    Vista para crear un nuevo producto con sus tallas e imágenes asociadas.
    Gestiona el formulario principal del producto y los formsets para tallas e imágenes.
    """
    if request.method == 'POST':
        # Imprimir información de depuración
        print("POST recibido para crear producto")
        print(f"Tallas TOTAL_FORMS: {request.POST.get('tallas-TOTAL_FORMS')}")
        print(f"Imágenes TOTAL_FORMS: {request.POST.get('imagenes-TOTAL_FORMS')}")
        
        # Crear formularios con los datos POST
        form = ProductoForm(request.POST, request.FILES)
        talla_formset = TallaFormSet(request.POST, prefix='tallas')
        imagen_formset = ImagenFormSet(request.POST, request.FILES, prefix='imagenes')
        
        # Validar formulario principal
        if form.is_valid():
            # Guardar producto primero para obtener un ID
            producto = form.save(commit=True)
            
            # Asignar el producto a los formsets
            talla_formset.instance = producto
            imagen_formset.instance = producto
            
            # Validar formsets de tallas e imágenes
            tallas_valid = talla_formset.is_valid()
            imagenes_valid = imagen_formset.is_valid()
            
            if not tallas_valid:
                print("Errores en formset de tallas:")
                for i, errors in enumerate(talla_formset.errors):
                    print(f"  Formulario {i}: {errors}")
                print(f"  Errores no de formulario: {talla_formset.non_form_errors()}")
            
            if not imagenes_valid:
                print("Errores en formset de imágenes:")
                for i, errors in enumerate(imagen_formset.errors):
                    print(f"  Formulario {i}: {errors}")
                print(f"  Errores no de formulario: {imagen_formset.non_form_errors()}")
            
            # Si ambos formsets son válidos, guardarlos
            if tallas_valid and imagenes_valid:
                talla_formset.save()
                imagen_formset.save()
                
                messages.success(request, f'Producto "{producto.nombre}" creado exitosamente')
                return redirect('catalogo:admin_lista_productos')
            else:
                # Si hay errores en los formsets, mostramos mensaje general
                messages.error(request, 'Por favor, corrige los errores en el formulario')
        else:
            # Si hay errores en el formulario principal
            print("Errores en formulario principal:", form.errors)
            messages.error(request, 'Por favor, corrige los errores en el formulario principal')
    else:
        # Para solicitudes GET, mostrar formularios vacíos
        form = ProductoForm()
        talla_formset = TallaFormSet(prefix='tallas')
        imagen_formset = ImagenFormSet(prefix='imagenes')
    
    # Renderizar plantilla con los formularios
    return render(request, 'catalogo/admin/editar_producto.html', {
        'form': form,
        'talla_formset': talla_formset,
        'imagen_formset': imagen_formset,
        'accion': 'Crear'
    })

# Editar producto existente
@login_required
@user_passes_test(es_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        # Datos para debug
        print("Management Form Fields en POST:")
        for key in request.POST:
            if 'tallas-' in key and 'FORMS' in key:
                print(f"  {key}: '{request.POST[key]}'")
        
        # Procesar el formulario
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        talla_formset = TallaFormSet(request.POST, instance=producto, prefix='tallas')
        imagen_formset = ImagenFormSet(request.POST, request.FILES, instance=producto, prefix='imagenes')
        
        # Validar todos los formularios
        form_valid = form.is_valid()
        talla_valid = talla_formset.is_valid()
        imagen_valid = imagen_formset.is_valid()
        
        if form_valid and talla_valid and imagen_valid:
            # Guardar todo
            producto = form.save()
            talla_formset.save()
            imagen_formset.save()
            cache_buster = str(int(time.time()))
            request.session['cache_buster'] = cache_buster
            messages.success(request, 'Producto actualizado completamente')
            return redirect('catalogo:admin_lista_productos')
        else:
            # Mostrar errores específicos
            if not form_valid:
                messages.error(request, 'Hay errores en la información básica del producto')
            if not talla_valid:
                messages.error(request, 'Hay errores en las tallas')
            if not imagen_valid:
                messages.error(request, 'Hay errores en las imágenes')
    else:
        form = ProductoForm(instance=producto)
        talla_formset = TallaFormSet(instance=producto, prefix='tallas')
        imagen_formset = ImagenFormSet(instance=producto, prefix='imagenes')
    
    return render(request, 'catalogo/admin/editar_producto.html', {
        'form': form,
        'talla_formset': talla_formset,
        'imagen_formset': imagen_formset,
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
    """
    Vista para listar productos con filtrado y paginación
    """
    # Obtener todos los productos
    productos_base = Producto.objects.select_related('categoria', 'marca').prefetch_related('imagenes')
    print(f"Total de productos en la base de datos: {productos_base.count()}")

    # Obtener todas las categorías y marcas para los filtros
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    
    # Obtener las categorías y marcas seleccionadas
    categorias_seleccionadas = request.GET.getlist('categoria')
    marcas_seleccionadas = request.GET.getlist('marca')
    
    # Aplicar filtros básicos sin usar django-filter
    productos_filtrados = productos_base
    
    # Filtrar por nombre
    nombre_busqueda = request.GET.get('nombre', '')
    if nombre_busqueda:
        productos_filtrados = productos_filtrados.filter(nombre__icontains=nombre_busqueda)
    
    # Filtrar por precio mínimo
    precio_min = request.GET.get('precio_min', '')
    if precio_min:
        try:
            productos_filtrados = productos_filtrados.filter(precio__gte=float(precio_min))
        except (ValueError, TypeError):
            pass
    
    # Filtrar por precio máximo
    precio_max = request.GET.get('precio_max', '')
    if precio_max:
        try:
            productos_filtrados = productos_filtrados.filter(precio__lte=float(precio_max))
        except (ValueError, TypeError):
            pass
    
    # Filtrar por categorías
    if categorias_seleccionadas:
        productos_filtrados = productos_filtrados.filter(categoria__id__in=categorias_seleccionadas)
    
    # Filtrar por marcas
    if marcas_seleccionadas:
        productos_filtrados = productos_filtrados.filter(marca__id__in=marcas_seleccionadas)
    
    # Filtrar por disponibilidad
    disponible = request.GET.get('disponible')
    if disponible == 'true':
        productos_filtrados = productos_filtrados.filter(disponible=True)
    
    print(f"Productos después de filtrar: {productos_filtrados.count()}")
    
    for producto in productos_filtrados:
        print(f"Producto: {producto.nombre} - Imagen principal: {producto.imagen}")
        print(f"  Imágenes asociadas: {producto.imagenes.count()}")
        
    # Paginar los resultados
    paginator = Paginator(productos_filtrados, 6)  # 6 productos por página
    page_number = request.GET.get('page', 1)
    
    try:
        productos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos_paginados,
        'categorias': categorias,
        'marcas': marcas,
        'categorias_seleccionadas': categorias_seleccionadas,
        'marcas_seleccionadas': marcas_seleccionadas,
        'nombre_busqueda': nombre_busqueda,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'disponible_seleccionado': disponible == 'true'
    })

def detalle_producto(request, producto_id):
    # Obtener un producto específico por su ID con todas sus relaciones
    producto = get_object_or_404(
        Producto.objects.select_related('categoria', 'marca')
                        .prefetch_related('imagenes', 'tallas'),
        id=producto_id, 
        disponible=True
    )
    
    # Obtener las imágenes ordenadas (primero la principal, luego por orden)
    # Limitar a máximo 10 imágenes para optimizar rendimiento
    imagenes = list(producto.imagenes.all().order_by('-es_principal', 'orden')[:10])
    
    # Si no hay imágenes, usar la imagen principal del modelo Producto
    if not imagenes and producto.imagen:
        # Crear un objeto tipo diccionario para mantener consistencia con la plantilla
        imagenes = [{
            'imagen': producto.imagen,
            'es_principal': True,
            'titulo': producto.nombre
        }]
    
    # Obtener productos relacionados (misma categoría, excluyendo el actual)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        disponible=True
    ).exclude(id=producto_id)[:4]  # Limitamos a 4 productos relacionados
    
    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
        'imagenes': imagenes,
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
    Vista para procesar solicitudes AJAX de DataTables y devolver datos de productos 
    paginados con soporte para filtrado por categoría y marca.
    """
    import time
    
    try:
        # Obtener los parámetros enviados por DataTables
        draw = int(request.POST.get('draw', 1))  # Contador de solicitudes
        start = int(request.POST.get('start', 0))  # Inicio de la paginación
        length = int(request.POST.get('length', 10))  # Cantidad de registros a mostrar
        search_value = request.POST.get('search[value]', '')  # Valor de búsqueda
        
        # Parámetros de filtros personalizados
        categoria_id = request.POST.get('categoria_id', '')
        marca_id = request.POST.get('marca_id', '')
        disponibilidad = request.POST.get('disponibilidad', '')
        
        # Configuración de orden
        order_column_index = request.POST.get('order[0][column]', '1')
        order_dir = request.POST.get('order[0][dir]', 'asc')
        
        # Mapeo de índices de columna a campos de la base de datos
        column_mapping = {
            '0': 'id',
            '1': 'nombre',
            '2': 'precio',
            '3': 'categoria__nombre',
            '4': 'marca__nombre',
            '5': 'stock',
            '6': 'disponible'
        }
        # Obtener el nombre del campo según el índice
        order_column = column_mapping.get(order_column_index, 'nombre')
        
        # Preparar el ordenamiento para orden descendente
        if order_dir == 'desc':
            order_column = f'-{order_column}'
        
        # Consulta base - todos los productos con sus relaciones
        queryset = Producto.objects.all().select_related('categoria', 'marca').prefetch_related('imagenes')
        
        # Aplicar filtros personalizados
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
            
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)
            
        if disponibilidad in ['0', '1']:
            queryset = queryset.filter(disponible=(disponibilidad == '1'))
        
        # Filtrar por término de búsqueda si existe
        if search_value:
            queryset = queryset.filter(
                Q(nombre__icontains=search_value) |
                Q(descripcion__icontains=search_value) |
                Q(categoria__nombre__icontains=search_value) |
                Q(marca__nombre__icontains=search_value)
            )
        
        # Contar registros para la paginación
        total_records = Producto.objects.count()  # Total sin filtrar
        total_records_filtered = queryset.count()  # Total después de filtrar
        
        # Ordenar y paginar los resultados
        queryset = queryset.order_by(order_column)[start:start + length]
        
        # Preparar los datos para la respuesta
        data = []
        for producto in queryset:
            # Obtener URL de la miniatura optimizada
            thumbnail_url = producto.get_thumbnail_url()
            
            # Estado de disponibilidad formateado como HTML
            if producto.disponible:
                disponible_html = '<span class="badge bg-success">Sí</span>'
            else:
                disponible_html = '<span class="badge bg-danger">No</span>'
            
            # URL de las acciones
            editar_url = reverse('catalogo:editar_producto', args=[producto.id])
            eliminar_url = reverse('catalogo:eliminar_producto', args=[producto.id])
            
            # Agregar HTML para previsualización de imagen más grande al hacer hover
            imagen_html = f'''
            <div class="thumbnail-container" style="position: relative;">
                <img src="{thumbnail_url}" alt="{producto.nombre}" 
                     width="60" height="60" class="img-thumbnail product-thumbnail"
                     style="object-fit: cover;" 
                     data-bs-toggle="tooltip" title="{producto.nombre}">
            </div>
            '''
            
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
                'imagen': imagen_html,
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
    
    except Exception as e:
        # Registrar el error para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en admin_productos_data: {str(e)}")
        
        # Devolver una respuesta de error formateada para DataTables
        return JsonResponse({
            'draw': draw if 'draw' in locals() else 1,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
            'error': str(e)
        }, status=500)