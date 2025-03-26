from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pedido, ItemPedido
from .forms import PedidoForm
from carrito.models import Carrito

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