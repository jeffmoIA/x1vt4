from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Pago, HistorialPago
import logging

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