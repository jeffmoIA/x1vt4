from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pedido, ItemPedido
from .forms import PedidoForm
from carrito.models import Carrito
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.views.generic import ListView

@login_required
def crear_pedido(request):
    """Crear un nuevo pedido a partir del carrito del usuario"""
    # Obtener el carrito del usuario
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    # Verificar si el carrito está vacío
    if not carrito.items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito:ver_carrito')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # Crear un nuevo pedido pero no guardarlo todavía
            pedido = form.save(commit=False)
            pedido.usuario = request.user
            pedido.save()
            
            # Transferir items del carrito al pedido
            for item in carrito.items.all():
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    precio=item.producto.precio,
                    cantidad=item.cantidad
                )
            
            # Vaciar el carrito
            carrito.items.all().delete()
            
            # Mostrar mensaje de éxito
            messages.success(request, 'Pedido realizado con éxito')
            
            # Redirigir a la página de detalles del pedido
            return redirect('pedidos:detalle_pedido', pedido_id=pedido.id)
    else:
        # Prellenar el formulario con la información del usuario si existe
        initial_data = {}
        if hasattr(request.user, 'perfil'):
            perfil = request.user.perfil
            initial_data = {
                'nombre_completo': request.user.get_full_name() or request.user.username,
                'direccion': perfil.direccion or '',
                'ciudad': perfil.ciudad or '',
                'codigo_postal': perfil.codigo_postal or '',
                'telefono': perfil.telefono or '',
            }
        form = PedidoForm(initial=initial_data)
    
    return render(request, 'pedidos/crear_pedido.html', {
        'form': form,
        'carrito': carrito
    })

@login_required
def lista_pedidos(request):
    """Mostrar todos los pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    return render(request, 'pedidos/lista_pedidos.html', {
        'pedidos': pedidos
    })

@login_required
def detalle_pedido(request, pedido_id):
    """Mostrar los detalles de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido': pedido
    })

@login_required
def cancelar_pedido(request, pedido_id):
    """Cancelar un pedido pendiente"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Solo se pueden cancelar pedidos pendientes
    if pedido.estado == 'pendiente':
        if request.method == 'POST':
            pedido.estado = 'cancelado'
            pedido.save()
            messages.success(request, 'Pedido cancelado exitosamente')
            return redirect('pedidos:lista_pedidos')
        
        return render(request, 'pedidos/confirmar_cancelacion.html', {
            'pedido': pedido
        })
    else:
        messages.error(request, 'Este pedido no puede ser cancelado')
        return redirect('pedidos:detalle_pedido', pedido_id=pedido.id)
    
def obtener_factura(request, pedido_id):
    """Vista para descargar la factura de un pedido"""
    # Verificar que el usuario esté autenticado
    if not request.user.is_authenticated:
        return redirect('usuarios:login')
    
    # Verificar que el pedido pertenece al usuario
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Importar la función desde utils
    from .utils import obtener_factura
    return obtener_factura(request, pedido_id)

# Función para verificar si el usuario es administrador
def es_admin(user):
    return user.is_staff

@login_required
@user_passes_test(es_admin)  # Solo administradores pueden acceder
def estadisticas_pedidos(request):
    """
    Vista para mostrar estadísticas de pedidos para administradores
    """
    # Obtener todos los pedidos
    pedidos = Pedido.objects.all()
    
    # Estadísticas generales
    total_pedidos = pedidos.count()
    pedidos_pendientes = pedidos.filter(estado=Pedido.PENDIENTE).count()
    pedidos_procesando = pedidos.filter(estado=Pedido.PROCESANDO).count()
    pedidos_enviados = pedidos.filter(estado=Pedido.ENVIADO).count()
    pedidos_entregados = pedidos.filter(estado=Pedido.ENTREGADO).count()
    pedidos_cancelados = pedidos.filter(estado=Pedido.CANCELADO).count()
    
    # Obtener pedidos por mes (últimos 6 meses)
    fecha_inicio = timezone.now() - timedelta(days=180)  # 6 meses atrás
    pedidos_por_mes_query = pedidos.filter(
        fecha_pedido__gte=fecha_inicio
    ).annotate(
        mes=TruncMonth('fecha_pedido')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')
    
    # Preparar datos para el gráfico de pedidos por mes
    meses = []
    totales = []
    
    for item in pedidos_por_mes_query:
        meses.append(item['mes'].strftime('%b %Y'))
        totales.append(item['total'])
    
    # Si no hay datos para algunos meses, llenar con ceros
    # Esto asegura que siempre mostramos 6 meses incluso si no hay pedidos
    if len(meses) < 6:
        fecha_actual = timezone.now()
        for i in range(6):
            fecha = fecha_actual - timedelta(days=30 * i)
            mes_str = fecha.strftime('%b %Y')
            if mes_str not in meses:
                meses.insert(0, mes_str)
                totales.insert(0, 0)
        # Limitar a solo 6 meses
        meses = meses[:6]
        totales = totales[:6]
    
    # Ordenar cronológicamente
    meses.reverse()
    totales.reverse()
    
    # Obtener pedidos recientes (últimos 10)
    pedidos_recientes = pedidos.order_by('-fecha_pedido')[:10]
    
    # Contexto para la plantilla
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_procesando': pedidos_procesando,
        'pedidos_enviados': pedidos_enviados,
        'pedidos_entregados': pedidos_entregados,
        'pedidos_cancelados': pedidos_cancelados,
        'meses_labels': json.dumps(meses),
        'pedidos_por_mes': totales,
        'pedidos_recientes': pedidos_recientes,
    }
    
    return render(request, 'pedidos/admin/estadisticas.html', context)

@login_required
@user_passes_test(es_admin)
def admin_lista_pedidos(request):
    """Vista para que los administradores gestionen todos los pedidos"""
    # Inicializar el queryset con todos los pedidos
    queryset = Pedido.objects.all().order_by('-fecha_pedido')
    
    # Aplicar filtros si existen
    estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if estado:
        queryset = queryset.filter(estado=estado)
    
    if fecha_desde:
        queryset = queryset.filter(fecha_pedido__date__gte=fecha_desde)
    
    if fecha_hasta:
        queryset = queryset.filter(fecha_pedido__date__lte=fecha_hasta)
    
    # Paginar los resultados
    paginator = Paginator(queryset, 10)  # Mostrar 10 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pedidos': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'pedidos/admin/lista_pedidos.html', context)

@login_required
@user_passes_test(es_admin)
def cambiar_estado_pedido(request, pedido_id):
    """Vista para que los administradores cambien el estado de un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in dict(Pedido.ESTADOS).keys():
            notas = f"Cambio realizado por el administrador {request.user.username}"
            pedido.cambiar_estado(nuevo_estado, notas)
            messages.success(request, f'Estado del pedido #{pedido.id} actualizado a {dict(Pedido.ESTADOS)[nuevo_estado]}')
        else:
            messages.error(request, 'Estado no válido')
    
    # Redirigir a la lista de pedidos manteniendo los filtros
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('pedidos:admin_lista_pedidos')
    
@login_required
@user_passes_test(es_admin)
def admin_detalle_pedido(request, pedido_id):
    """Vista detallada de pedido para administradores"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Obtener el historial de estados del pedido
    historial = pedido.historial_estados.all().order_by('-fecha_cambio')
    
    context = {
        'pedido': pedido,
        'historial': historial,
    }
    
    return render(request, 'pedidos/admin/detalle_pedido.html', context)

@login_required
@user_passes_test(es_admin)
def actualizar_seguimiento(request, pedido_id):
    """Actualizar información de seguimiento de un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        # Actualizar los campos de seguimiento
        pedido.empresa_envio = request.POST.get('empresa_envio', '')
        pedido.codigo_seguimiento = request.POST.get('codigo_seguimiento', '')
        pedido.save()
        
        messages.success(request, f'Información de seguimiento del pedido #{pedido.id} actualizada')
    
    return redirect('pedidos:admin_detalle_pedido', pedido_id=pedido.id)
    