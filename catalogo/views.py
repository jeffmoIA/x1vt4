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
from django.views.decorators.http import require_POST
from .models import Marca
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from utils.performance import query_debugger
from django.core.cache import cache
from django.views.decorators.cache import cache_page

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
    if request.method == 'POST':
        # Depuración
        print("FILES:", request.FILES)
        
        form = ProductoForm(request.POST, request.FILES)
        talla_formset = TallaFormSet(request.POST, prefix='tallas')
        imagen_formset = ImagenFormSet(request.POST, request.FILES, prefix='imagenes')
        
        # Validar formularios
        form_valid = form.is_valid()
        tallas_valid = talla_formset.is_valid() 
        imagenes_valid = imagen_formset.is_valid()
        
        print(f"Principal: {form_valid}, Tallas: {tallas_valid}, Imágenes: {imagenes_valid}")
        
        if form_valid and tallas_valid and imagenes_valid:
            producto = form.save()
            talla_formset.instance = producto
            imagen_formset.instance = producto
            talla_formset.save()
            imagen_formset.save()
            
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente')
            return redirect('catalogo:admin_lista_productos')
        else:
            # Mostrar errores
            print("Errores en el formulario principal:", form.errors)
            print("Errores en imágenes:", imagen_formset.errors)
            for i, f in enumerate(imagen_formset):
                print(f"Formulario {i}:", f.errors)
    else:
        form = ProductoForm()
        talla_formset = TallaFormSet(prefix='tallas')
        imagen_formset = ImagenFormSet(prefix='imagenes')
    
    return render(request, 'catalogo/admin/crear_producto.html', {
        'form': form,
        'talla_formset': talla_formset,
        'imagen_formset': imagen_formset
    })


# Editar producto existente
@login_required
@user_passes_test(es_admin)
def editar_producto(request, producto_id):
    """
    Vista para editar un producto existente con las siguientes funcionalidades:
    - Aplicar cambios: Guarda los cambios sin redireccionar, permaneciendo en el formulario
    - Guardar y salir: Guarda los cambios y redirecciona a la lista de productos
    """
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        # Determinar tipo de solicitud
        es_aplicar_cambios = 'aplicar_cambios' in request.POST
        debe_redirigir = 'redirigir' in request.POST
        
        # Procesar formularios
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        talla_formset = TallaFormSet(request.POST, instance=producto, prefix='tallas')
        imagen_formset = ImagenFormSet(request.POST, request.FILES, instance=producto, prefix='imagenes')
        
        # Si los formsets son válidos, guardar
        todos_validos = all([
            form.is_valid(),
            talla_formset.is_valid(),
            imagen_formset.is_valid()
        ])
        
        if todos_validos:
            # Guardar todo
            producto = form.save()
            talla_formset.save()
            imagen_formset.save()
            
            # COMPORTAMIENTO CORREGIDO: Solo redirigir si es "guardar y salir"
            if debe_redirigir:
                messages.success(request, 'Producto guardado correctamente')
                return redirect('catalogo:admin_lista_productos')
            
            # Para "aplicar cambios", mostrar mensaje pero permanecer en la misma página
            if es_aplicar_cambios:
                messages.success(request, 'Cambios aplicados correctamente')
                # Redirigir a la misma página para refrescar el formulario con los cambios
                return redirect('catalogo:editar_producto', producto_id=producto.id)
            
            # Por defecto
            messages.success(request, 'Producto actualizado correctamente')
        else:
            # Si hay errores, mostrar mensajes
            messages.error(request, 'Hay errores en el formulario')
    else:
        # Para solicitudes GET
        form = ProductoForm(instance=producto)
        talla_formset = TallaFormSet(instance=producto, prefix='tallas')
        imagen_formset = ImagenFormSet(instance=producto, prefix='imagenes')
    
    # Renderizar plantilla
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

@cache_page(60 * 15)  # 15 minutos
@query_debugger  # Para analizar el rendimiento de las consultas
def lista_productos(request):
    """
    Vista para listar productos con filtrado y paginación
    """
    # Uso de select_related para cargar de una vez las relaciones ForeignKey
    # prefetch_related para las relaciones ManyToMany e imágenes
    productos_base = (Producto.objects
                     .select_related('categoria', 'marca')  # Carga en una sola consulta
                     .prefetch_related(
                         'imagenes',  # Carga todas las imágenes en una sola consulta
                         'tallas'     # Carga todas las tallas en una sola consulta
                     ))
    
    # Inicializar productos_filtrados con productos_base
    productos_filtrados = productos_base  # Esta es la línea clave que faltaba
    
    # Aplicamos filtros según los parámetros de GET
    # Nota: Aquí usamos el procesamiento diferido de Django ORM,
    # que no ejecuta consultas hasta que realmente se necesiten los datos
    
    # Filtrar por nombre
    nombre_busqueda = request.GET.get('nombre', '')
    if nombre_busqueda:
        productos_filtrados = productos_filtrados.filter(nombre__icontains=nombre_busqueda)
    
    # Categorías y marcas para los filtros laterales (esto se puede cachear)
    from django.core.cache import cache
    
    # Intentar obtener categorías de la caché
    categorias = cache.get('todas_categorias')
    if categorias is None:
        categorias = Categoria.objects.all()
        # Guardar en caché por 1 hora (3600 segundos)
        cache.set('todas_categorias', categorias, 3600)
    
    # Intentar obtener marcas de la caché
    marcas = cache.get('todas_marcas')
    if marcas is None:
        marcas = Marca.objects.all()
        # Guardar en caché por 1 hora
        cache.set('todas_marcas', marcas, 3600)
    
    # Filtros adicionales por precio, categoría, marca y disponibilidad
    # Filtrar por rango de precios
    precio_min = request.GET.get('precio_min')
    if precio_min:
        try:
            productos_filtrados = productos_filtrados.filter(precio__gte=float(precio_min))
        except (ValueError, TypeError):
            pass  # Ignorar si no es un número válido
    
    precio_max = request.GET.get('precio_max')
    if precio_max:
        try:
            productos_filtrados = productos_filtrados.filter(precio__lte=float(precio_max))
        except (ValueError, TypeError):
            pass  # Ignorar si no es un número válido
    
    # Filtrar por categorías seleccionadas
    categorias_seleccionadas = request.GET.getlist('categoria')
    if categorias_seleccionadas:
        productos_filtrados = productos_filtrados.filter(categoria__id__in=categorias_seleccionadas)
    
    # Filtrar por marcas seleccionadas
    marcas_seleccionadas = request.GET.getlist('marca')
    if marcas_seleccionadas:
        productos_filtrados = productos_filtrados.filter(marca__id__in=marcas_seleccionadas)
    
    # Filtrar por disponibilidad
    disponible = request.GET.get('disponible')
    if disponible == 'true':
        productos_filtrados = productos_filtrados.filter(disponible=True)
    
    # Añadir orden explícito antes de paginar para evitar la advertencia
    productos_filtrados = productos_filtrados.order_by('-id')
    
    # Paginar los resultados - usamos el paginador eficiente de Django
    paginator = Paginator(productos_filtrados, 6)  # 6 productos por página
    page_number = request.GET.get('page', 1)
    
    try:
        productos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    # El contexto que se pasa a la plantilla
    context = {
        'productos': productos_paginados,
        'categorias': categorias,
        'marcas': marcas,
        'categorias_seleccionadas': categorias_seleccionadas,
        'marcas_seleccionadas': marcas_seleccionadas,
        'nombre_busqueda': nombre_busqueda,
        'precio_min': precio_min or '',
        'precio_max': precio_max or '',
        'disponible_seleccionado': disponible == 'true'
    }
    
    return render(request, 'catalogo/lista_productos.html', context)

@query_debugger
def detalle_producto(request, producto_id):
    """
    Vista optimizada para mostrar detalles de un producto específico
    """
    # Obtener un producto específico por su ID con todas sus relaciones en una sola consulta
    producto = get_object_or_404(
        Producto.objects.select_related('categoria', 'marca')
                        .prefetch_related(
                            Prefetch('imagenes', queryset=ImagenProducto.objects.order_by('-es_principal', 'orden')),
                            'tallas'
                        ),
        id=producto_id, 
        disponible=True
    )
    
    # Obtenemos directamente las imágenes ya ordenadas gracias al Prefetch
    imagenes = list(producto.imagenes.all()[:10])
    
    # Clave de caché única para productos relacionados
    cache_key = f'productos_relacionados_{producto_id}'
    
    # Intentar obtener productos relacionados de la caché
    productos_relacionados = cache.get(cache_key)
    if productos_relacionados is None:
        # Si no están en caché, ejecutamos la consulta
        productos_relacionados = list(
            Producto.objects.filter(
                categoria=producto.categoria,
                disponible=True
            ).exclude(id=producto_id)[:4]  # Limitamos a 4 productos relacionados
        )
        # Guardamos en caché por 1 hora
        cache.set(cache_key, productos_relacionados, 3600)
    
    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
        'imagenes': imagenes,
        'productos_relacionados': productos_relacionados
    })

@cache_page(60 * 30)  # Caché de 30 minutos
def productos_populares(request):
    """
    Vista optimizada que muestra productos populares o más vistos
    con caché eficiente
    """
    # Intentar obtener datos de caché
    cache_key = 'productos_populares'
    productos = cache.get(cache_key)
    
    if productos is None:
        # Si no están en caché, consultar la base de datos
        # Esta consulta simula productos populares (en un sistema real
        # se usarían datos de vistas o compras)
        productos = list(Producto.objects
                        .filter(disponible=True)
                        .order_by('-stock')  # Productos más disponibles
                        .select_related('categoria', 'marca')
                        .prefetch_related('imagenes')[:12])
        
        # Guardar en caché por 30 minutos
        cache.set(cache_key, productos, 60 * 30)
    
    return render(request, 'catalogo/productos_populares.html', {
        'productos': productos,
        'titulo': 'Productos Populares'
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
@csrf_exempt
@query_debugger
def admin_productos_data(request):
    """
    Vista optimizada para cargar datos de productos mediante AJAX para DataTables
    """
    try:
        if request.method == 'POST':
            # Parámetros de DataTables
            draw = int(request.POST.get('draw', 1))
            start = int(request.POST.get('start', 0))
            length = int(request.POST.get('length', 10))
            search_value = request.POST.get('search[value]', '')
            
            # Filtros específicos
            categoria_id = request.POST.get('categoria_id', '')
            marca_id = request.POST.get('marca_id', '')
            disponibilidad = request.POST.get('disponibilidad', '')
            
            # Configuración de orden
            order_column_index = request.POST.get('order[0][column]', '1')
            order_dir = request.POST.get('order[0][dir]', 'asc')
            
            # Mapeo de columnas
            column_mapping = {
                '0': 'id', '1': 'nombre', '2': 'precio',
                '3': 'categoria__nombre', '4': 'marca__nombre',
                '5': 'stock', '6': 'disponible'
            }
            
            order_column = column_mapping.get(order_column_index, 'nombre')
            if order_dir == 'desc':
                order_column = f'-{order_column}'
            
            # Consulta base optimizada
            queryset = (Producto.objects
                        .select_related('categoria', 'marca')
                        .prefetch_related('imagenes'))
            
            # Aplicar filtros
            if categoria_id and categoria_id != '':
                queryset = queryset.filter(categoria_id=categoria_id)
                
            if marca_id and marca_id != '':
                queryset = queryset.filter(marca_id=marca_id)
                
            if disponibilidad in ['0', '1']:
                queryset = queryset.filter(disponible=(disponibilidad == '1'))
            
            # Filtrar por término de búsqueda
            if search_value:
                queryset = queryset.filter(
                    Q(nombre__icontains=search_value) |
                    Q(descripcion__icontains=search_value) |
                    Q(categoria__nombre__icontains=search_value) |
                    Q(marca__nombre__icontains=search_value)
                )
            
            # Contar registros una sola vez y cachear resultados
            cache_key = f'productos_total_count_{categoria_id}_{marca_id}_{disponibilidad}'
            total_records = cache.get(cache_key)
            if total_records is None:
                total_records = Producto.objects.count()
                cache.set(cache_key, total_records, 60 * 15)  # 15 minutos
            
            # Total filtrado - esto es más dinámico y difícil de cachear
            total_records_filtered = queryset.count()
            
            # Aplicar ordenamiento y paginación eficientemente
            paginated_queryset = queryset.order_by(order_column)[start:start + length]
            
            # Preparar datos para JSON (optimizando la generación de HTML)
            data = []
            for producto in paginated_queryset:
                # Renderizar todos los componentes en una sola pasada
                data.append({
                    'imagen': f'<img src="{producto.get_thumbnail_url()}" alt="{producto.nombre}" width="60" height="60" class="img-thumbnail">',
                    'nombre': producto.nombre,
                    'precio': f'${producto.precio}',
                    'categoria': producto.categoria.nombre,
                    'marca': producto.marca.nombre,
                    'stock': producto.stock,
                    'disponible': '<span class="badge bg-success">Sí</span>' if producto.disponible else '<span class="badge bg-danger">No</span>',
                    'acciones': f"""
                        <div class="btn-group">
                            <a href="{reverse('catalogo:editar_producto', args=[producto.id])}" class="btn btn-sm btn-warning">
                                <i class="fas fa-edit"></i>
                            </a>
                            <a href="{reverse('catalogo:eliminar_producto', args=[producto.id])}" class="btn btn-sm btn-danger">
                                <i class="fas fa-trash"></i>
                            </a>
                        </div>
                    """
                })
            
            # Respuesta JSON eficiente
            response_data = {
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records_filtered,
                'data': data
            }
            
            # Configurar headers CORS para permitir peticiones desde cualquier origen
            response = JsonResponse(response_data)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type, X-CSRFToken"
            
            return response
        
    except Exception as e:
        # Log del error para diagnóstico
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error en admin_productos_data: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Respuesta de error
        return JsonResponse({
            'draw': 1,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
            'error': str(e)
        }, status=500)
        
@login_required
@user_passes_test(es_admin)
def listar_marcas_ajax(request):
    """
    Vista mejorada para listar todas las marcas en formato JSON,
    incluyendo conteo de productos para cada marca.
    """
    try:
        # Obtener todas las marcas ordenadas por nombre
        marcas = Marca.objects.all().order_by('nombre')
        
        # Crear lista de diccionarios con id, nombre y conteo de productos
        marcas_list = []
        for marca in marcas:
            productos_count = marca.productos.count()
            marcas_list.append({
                'id': marca.id, 
                'nombre': marca.nombre,
                'productos_count': productos_count
            })
        
        # Retornar como JSON
        return JsonResponse({'success': True, 'marcas': marcas_list})
    except Exception as e:
        # En caso de error, registrar y retornar mensaje
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al listar marcas: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(es_admin)
@require_POST  # Asegúrate de importar require_POST de django.views.decorators.http
def crear_marca_ajax(request):
    """
    Vista para crear una nueva marca mediante AJAX.
    """
    try:
        # Obtener el nombre de la marca desde la solicitud POST
        nombre = request.POST.get('nombre', '').strip()
        
        # Validación básica
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre de la marca es requerido'}, status=400)
        
        # Verificar si ya existe una marca con ese nombre
        if Marca.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe una marca con ese nombre'}, status=400)
        
        # Crear la nueva marca
        marca = Marca.objects.create(nombre=nombre)
        
        # Retornar respuesta exitosa con los datos de la marca
        return JsonResponse({
            'success': True, 
            'id': marca.id, 
            'nombre': marca.nombre,
            'message': f'La marca "{marca.nombre}" ha sido creada exitosamente'
        })
    except Exception as e:
        # En caso de error, registrar y retornar mensaje
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al crear marca: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(es_admin)
@require_POST
def eliminar_marca_ajax(request):
    """
    Vista para eliminar una marca mediante AJAX.
    """
    try:
        # Obtener el ID de la marca
        marca_id = request.POST.get('id')
        
        # Validación básica
        if not marca_id:
            return JsonResponse({'success': False, 'error': 'ID de marca no proporcionado'}, status=400)
        
        # Obtener la marca o devolver 404
        marca = get_object_or_404(Marca, id=marca_id)
        
        # Verificar si hay productos asociados a esta marca
        if marca.productos.exists():
            return JsonResponse({
                'success': False, 
                'error': f'No se puede eliminar la marca "{marca.nombre}" porque tiene productos asociados'
            }, status=400)
        
        # Guardar el nombre para el mensaje de confirmación
        nombre_marca = marca.nombre
        
        # Eliminar la marca
        marca.delete()
        
        # Retornar respuesta exitosa
        return JsonResponse({
            'success': True,
            'message': f'La marca "{nombre_marca}" ha sido eliminada exitosamente'
        })
    except Exception as e:
        # En caso de error, registrar y retornar mensaje
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al eliminar marca: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)