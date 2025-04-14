from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Carrito, ItemCarrito
from utils.cache_utils import invalidate_model_cache

# Signals para Carrito
@receiver(post_save, sender=Carrito)
def carrito_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda un carrito"""
    invalidate_model_cache('carrito', instance.usuario.id)
    
@receiver(post_delete, sender=Carrito)
def carrito_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un carrito"""
    invalidate_model_cache('carrito', instance.usuario.id)

# Signals para ItemCarrito
@receiver(post_save, sender=ItemCarrito)
def item_carrito_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se modifica un item del carrito"""
    invalidate_model_cache('carrito', instance.carrito.usuario.id)
    
@receiver(post_delete, sender=ItemCarrito)
def item_carrito_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un item del carrito"""
    invalidate_model_cache('carrito', instance.carrito.usuario.id)