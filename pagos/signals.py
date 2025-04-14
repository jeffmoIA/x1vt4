from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Pago, HistorialPago
import logging
from utils.cache_utils import invalidate_model_cache

logger = logging.getLogger('mototienda.security')

@receiver(post_save, sender=Pago)
def log_pago_changes(sender, instance, created, **kwargs):
    """Registra cambios en pagos para monitoreo de seguridad."""
    if created:
        logger.info(f"Nuevo pago creado: ID {instance.id}, Referencia {instance.referencia}, " +
                   f"Monto ${instance.monto}, Estado {instance.status}")
    else:
        logger.info(f"Pago actualizado: ID {instance.id}, Referencia {instance.referencia}, " +
                   f"Monto ${instance.monto}, Estado {instance.status}")

@receiver(post_save, sender=HistorialPago)
def log_historial_pago(sender, instance, created, **kwargs):
    """Registra cambios en historiales de pago para auditoría."""
    if created:
        logger.info(f"Cambio de estado en pago {instance.pago.referencia}: " +
                   f"{instance.estado_anterior} → {instance.estado_nuevo}")
        
        # Alertar específicamente sobre reembolsos o pagos fallidos
        if instance.estado_nuevo in ['fallido', 'reembolsado']:
            logger.warning(f"ALERTA: Pago {instance.pago.referencia} cambió a estado {instance.estado_nuevo}")

# Signals para Pago
@receiver(post_save, sender=Pago)
def pago_saved(sender, instance, created, **kwargs):
    """Invalidar caché cuando se guarda un pago"""
    invalidate_model_cache('pedido', instance.pedido.id)
    
@receiver(post_delete, sender=Pago)
def pago_deleted(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un pago"""
    invalidate_model_cache('pedido', instance.pedido.id)