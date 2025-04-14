from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Pedido, ItemPedido
from utils.cache_utils import invalidate_model_cache

# Signals para Pedido
@receiver(post_save, sender=Pedido)
def pedido_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda un pedido"""
    invalidate_model_cache('pedido', instance.id)
    
    # También invalidamos estadísticas generales
    invalidate_model_cache('estadisticas_pedidos')
    
@receiver(post_delete, sender=Pedido)
def pedido_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un pedido"""
    invalidate_model_cache('pedido', instance.id)
    invalidate_model_cache('estadisticas_pedidos')

# Signals para ItemPedido
@receiver(post_save, sender=ItemPedido)
def item_pedido_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda un item de pedido"""
    invalidate_model_cache('pedido', instance.pedido.id)
    
@receiver(post_delete, sender=ItemPedido)
def item_pedido_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un item de pedido"""
    invalidate_model_cache('pedido', instance.pedido.id)