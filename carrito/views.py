from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Producto, TallaProducto
from .models import Carrito, ItemCarrito
from django.http import JsonResponse

@login_required  # Solo usuarios autenticados pueden ver su carrito
def ver_carrito(request):
    # Vista para mostrar el contenido del carrito
    # get_or_create devuelve el carrito existente o crea uno nuevo si no existe
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    return render(request, 'carrito/carrito.html', {'carrito': carrito})

@login_required
def agregar_al_carrito(request, producto_id):
    # Obtener el producto o devolver 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Determinar la cantidad y otras opciones del producto
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        talla = request.POST.get('talla', '')
        color = request.POST.get('color', '')
        # Obtener el valor del botón de "comprar ahora"
        comprar_ahora = request.POST.get('comprar_ahora', '') == '1'
    else:
        cantidad = 1
        talla = ''
        color = ''
        # Para solicitudes GET, verificar si se incluye un parámetro de redirección
        comprar_ahora = request.GET.get('redirect') == 'checkout'
    
    # Si el usuario está autenticado, obtener o crear su carrito
    if request.user.is_authenticated:
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
        
        # Buscar si el producto ya está en el carrito con las mismas opciones
        try:
            item = ItemCarrito.objects.get(
                carrito=carrito,
                producto=producto,
                talla=talla,
                color=color
            )
            # Si existe, aumentar la cantidad
            item.cantidad += cantidad
            item.save()
        except ItemCarrito.DoesNotExist:
            # Si no existe, crear uno nuevo
            ItemCarrito.objects.create(
                carrito=carrito,
                producto=producto,
                cantidad=cantidad,
                talla=talla,
                color=color
            )
        
        # Redirigir según la acción
        if comprar_ahora:
            return redirect('pedidos:crear_pedido')
        else:
            return redirect('carrito:ver_carrito')
    else:
        # Si no está autenticado, redirigir a login
        return redirect('usuarios:login')

@login_required
def actualizar_carrito(request, item_id):
    """Actualiza la cantidad de un ítem en el carrito"""
    if not request.user.is_authenticated:
        return redirect('usuarios:login')
        
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    carrito = item.carrito
    
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            
            if cantidad > 0:
                if cantidad <= item.producto.stock:
                    # Actualizar la cantidad
                    item.cantidad = cantidad
                    item.save()
                    
                    # Si es una solicitud AJAX, devolver JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'subtotal': float(item.subtotal()),
                            'total': float(carrito.total()),
                            'items_count': carrito.items.count()
                        })
                else:
                    # No hay suficiente stock
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': f'Solo hay {item.producto.stock} unidades disponibles',
                            'current_quantity': item.cantidad
                        })
            else:
                # Si la cantidad es 0 o negativa, eliminar el ítem
                item.delete()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'deleted': True,
                        'total': float(carrito.total()),
                        'items_count': carrito.items.count()
                    })
                    
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Cantidad inválida',
                    'current_quantity': item.cantidad
                })
    
    # Para solicitudes no AJAX, redirigir a la página del carrito
    return redirect('carrito:ver_carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    # Vista para eliminar un producto del carrito
    # Obtener el item asegurándose que pertenece al usuario actual
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    # Eliminar el item
    item.delete()
    # Redirigir a la vista del carrito
    return redirect('carrito:ver_carrito')