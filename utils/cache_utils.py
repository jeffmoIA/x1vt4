from django.core.cache import cache
import logging

logger = logging.getLogger('mototienda.performance')

def invalidate_model_cache(model_name, object_id=None):
    """
    Invalida todas las cachés relacionadas con un modelo específico
    o un objeto específico.
    
    Args:
        model_name (str): Nombre del modelo (ej: 'producto', 'categoria')
        object_id (int, optional): ID específico del objeto a invalidar
    """
    # Mapeo de patrones de clave de caché por modelo
    cache_patterns = {
        'producto': [
            'productos_*',
            f'producto_{object_id}*' if object_id else None,
            'catalogo_*',
        ],
        'categoria': [
            'todas_categorias',
            'catalogo_*',
            f'categoria_{object_id}*' if object_id else None,
        ],
        'marca': [
            'todas_marcas',
            'catalogo_*',
            f'marca_{object_id}*' if object_id else None,
        ],
        'pedido': [
            f'pedido_{object_id}*' if object_id else None,
            'estadisticas_pedidos*',
        ],
        'carrito': [
            f'carrito_count_{object_id}*' if object_id else None,
        ],
    }
    
    # Obtener patrones para el modelo especificado
    patterns = cache_patterns.get(model_name.lower(), [])
    patterns = [p for p in patterns if p]  # Eliminar None
    
    # Log para depuración
    logger.debug(f"Invalidando caché para {model_name}" + 
                (f" ID: {object_id}" if object_id else ""))
    
    # Eliminar cachés que coincidan con los patrones
    for pattern in patterns:
        if '*' in pattern:
            # Si tiene wildcard, necesitamos buscar todas las claves que coincidan
            # Esto depende de cómo está implementado el backend de caché
            # En Redis puedes usar KEYS, pero eso es costoso en producción
            # Aquí una implementación simplificada que funciona mejor con Memcached
            keys = []
            if hasattr(cache, 'keys'):
                # Si el backend de caché soporta listar claves
                all_keys = cache.keys(pattern)
                keys.extend(all_keys)
            else:
                # Si no, no podemos hacer mucho
                logger.warning(f"Backend de caché no soporta wildcards. Patrón: {pattern}")
                
            # Eliminar cada clave encontrada
            for key in keys:
                cache.delete(key)
                logger.debug(f"  Caché invalidada: {key}")
        else:
            # Si es una clave exacta, simplemente la eliminamos
            cache.delete(pattern)
            logger.debug(f"  Caché invalidada: {pattern}")

def invalidate_all_cache():
    """Invalida toda la caché del sistema"""
    logger.info("Invalidando toda la caché del sistema")
    cache.clear()
