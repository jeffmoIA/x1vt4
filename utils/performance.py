# Utilidad para medir y optimizar el rendimiento de consultas en la base de datos
import time
import functools
import logging
from django.db import connection, reset_queries
from django.conf import settings

logger = logging.getLogger('mototienda.performance')

def query_debugger(func):
    """
    Decorador que registra el número de consultas ejecutadas en una función
    y el tiempo total de ejecución.
    
    Uso:
        @query_debugger
        def mi_vista(request):
            ...
    """
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        # Solo si estamos en modo DEBUG
        if settings.DEBUG:
            reset_queries()  # Reinicia el contador de consultas
            
            # Mide el tiempo de inicio
            start_time = time.time()
            
            # Ejecuta la función original
            result = func(*args, **kwargs)
            
            # Mide el tiempo de finalización
            end_time = time.time()
            
            # Calcula tiempo total y número de consultas
            total_time = end_time - start_time
            queries_count = len(connection.queries)
            
            # Registra los resultados
            logger.debug(f"Función '{func.__name__}': {queries_count} consultas en {total_time:.2f} segundos")
            
            # Si hay demasiadas consultas, registra un warning
            if queries_count > 50:
                logger.warning(f"¡Posible N+1 en '{func.__name__}'! {queries_count} consultas")
                
                # En modo debug, muestra las consultas para diagnóstico
                if settings.DEBUG:
                    for i, query in enumerate(connection.queries):
                        logger.debug(f"Consulta {i+1}: {query['sql']}")
            
            return result
        else:
            # En producción simplemente ejecuta la función
            return func(*args, **kwargs)
    return inner_func

def get_optimized_queryset(queryset, batch_size=100):
    """
    Procesa un queryset en lotes para evitar problemas de memoria con grandes conjuntos de datos.
    
    Args:
        queryset: El queryset a procesar
        batch_size: Tamaño del lote (por defecto 100)
        
    Yields:
        Objetos del queryset en lotes
    """
    start = 0
    while True:
        # Obtiene un lote de objetos
        batch = list(queryset[start:start + batch_size])
        if not batch:
            break
            
        # Proporciona los objetos uno a uno
        for obj in batch:
            yield obj
            
        # Actualiza el índice de inicio para el siguiente lote
        start += batch_size