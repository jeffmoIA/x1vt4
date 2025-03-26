from .models import Carrito

def carrito_count(request):
    """
    Procesador de contexto que añade el número de elementos en el carrito
    a todas las plantillas.
    """
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            # Contar el número total de elementos (sumando las cantidades)
            count = sum(item.cantidad for item in carrito.items.all())
            return {'carrito_count': count}
        except Carrito.DoesNotExist:
            pass
    return {'carrito_count': 0}