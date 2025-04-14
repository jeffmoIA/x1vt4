from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Categoria, Marca, Producto, TallaProducto, ImagenProducto
from utils.cache_utils import invalidate_model_cache

# Signals para Categoria
@receiver(post_save, sender=Categoria)
def categoria_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda una categoría"""
    invalidate_model_cache('categoria', instance.id)
    
@receiver(post_delete, sender=Categoria)
def categoria_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina una categoría"""
    invalidate_model_cache('categoria', instance.id)

# Signals para Marca
@receiver(post_save, sender=Marca)
def marca_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda una marca"""
    invalidate_model_cache('marca', instance.id)
    
@receiver(post_delete, sender=Marca)
def marca_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina una marca"""
    invalidate_model_cache('marca', instance.id)

# Signals para Producto
@receiver(post_save, sender=Producto)
def producto_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda un producto"""
    invalidate_model_cache('producto', instance.id)
    
@receiver(post_delete, sender=Producto)
def producto_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un producto"""
    invalidate_model_cache('producto', instance.id)

# Signals para TallaProducto
@receiver(post_save, sender=TallaProducto)
def talla_producto_saved(sender, instance, created, **kwargs):
    """Invalidar caché de producto cuando se guarda una talla"""
    invalidate_model_cache('producto', instance.producto.id)
    
@receiver(post_delete, sender=TallaProducto)
def talla_producto_deleted(sender, instance, **kwargs):
    """Invalidar caché de producto cuando se elimina una talla"""
    invalidate_model_cache('producto', instance.producto.id)

# Signals para ImagenProducto
@receiver(post_save, sender=ImagenProducto)
def imagen_producto_saved(sender, instance, created, **kwargs):
    """Invalidar caché de producto cuando se guarda una imagen"""
    invalidate_model_cache('producto', instance.producto.id)
    
@receiver(post_delete, sender=ImagenProducto)
def imagen_producto_deleted(sender, instance, **kwargs):
    """Invalidar caché de producto cuando se elimina una imagen"""
    invalidate_model_cache('producto', instance.producto.id)