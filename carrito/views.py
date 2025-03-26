from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from catalogo.models import Producto
from .models import Carrito, ItemCarrito

@login_required  # Solo usuarios autenticados pueden ver su carrito
def ver_carrito(request):
    # Vista para mostrar el contenido del carrito
    # get_or_create devuelve el carrito existente o crea uno nuevo si no existe
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    return render(request, 'carrito/carrito.html', {'carrito': carrito})

@login_required
def agregar_al_carrito(request, producto_id):
    # Vista para añadir un producto al carrito
    # Obtener el producto o devolver 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)
    # Obtener o crear el carrito del usuario
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    # Buscar si el producto ya está en el carrito
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': 1}  # Si es nuevo, establecer cantidad 1
    )
    
    # Si el producto ya existía en el carrito, aumentar la cantidad
    if not creado:
        item.cantidad += 1
        item.save()
    
    # Redirigir a la vista del carrito
    return redirect('carrito:ver_carrito')

@login_required
def actualizar_carrito(request, item_id):
    # Vista para actualizar la cantidad de un producto en el carrito
    # Obtener el item asegurándose que pertenece al usuario actual
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    
    if request.method == 'POST':
        # Obtener la nueva cantidad del formulario
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad > 0:
            # Si es mayor que cero, actualizar la cantidad
            item.cantidad = cantidad
            item.save()
        else:
            # Si es cero o negativo, eliminar el item
            item.delete()
    
    # Redirigir a la vista del carrito
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