from .models import Carrito
from django.core.cache import cache

def carrito_count(request):
    """
    Procesador de contexto que añade el número de elementos en el carrito
    a todas las plantillas, optimizado con caché.
    """
    # Solo procesamos para usuarios autenticados
    if request.user.is_authenticated:
        # Intentamos obtener el conteo desde la caché
        cache_key = f'carrito_count_{request.user.id}'
        count = cache.get(cache_key)
        
        # Si no está en caché, calculamos el valor
        if count is None:
            try:
                carrito = Carrito.objects.get(usuario=request.user)
                # Usamos una sola consulta para obtener el total sumando cantidades
                count = carrito.items.aggregate(total=models.Sum('cantidad'))['total'] or 0
                
                # Guardamos en caché por un tiempo corto (2 minutos)
                # Este valor se refresca frecuentemente
                cache.set(cache_key, count, 120)
            except Carrito.DoesNotExist:
                count = 0
                
        return {'carrito_count': count}
        
    # Para usuarios no autenticados siempre devolvemos 0
    return {'carrito_count': 0}