from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from pedidos.models import Pedido
import uuid
import hashlib
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger('mototienda.security')

class MetodoPago(models.Model):
    """
    Modelo para representar métodos de pago disponibles en el sistema.
    """
    TIPOS = (
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
        ('efectivo', 'Pago contra entrega'),
    )
    
    nombre = models.CharField(max_length=100)  # Nombre descriptivo del método de pago
    tipo = models.CharField(max_length=20, choices=TIPOS)  # Tipo de método de pago
    activo = models.BooleanField(default=True)  # Indica si el método está disponible
    comision = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Comisión aplicable (%)
    descripcion = models.TextField(blank=True, null=True)  # Descripción o instrucciones
    
    def __str__(self):
        return self.nombre

class Pago(models.Model):
    """
    Modelo que registra los pagos realizados, sin almacenar datos sensibles
    de tarjetas conforme a PCI DSS.
    """
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    )
    
    # Identificador único para el pago
    referencia = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Relaciones
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    
    # Información del pago
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Detalles adicionales que no incluyen datos sensibles
    transaccion_id = models.CharField(max_length=255, blank=True, null=True)  # ID externo del procesador
    gateway_usado = models.CharField(max_length=50, blank=True)  # Procesador usado (simulado, stripe, etc.)
    
    # Campo para posibles notas administrativas
    notas = models.TextField(blank=True, null=True)
    
    # Suma de verificación para detectar manipulaciones (seguridad adicional)
    checksum = models.CharField(max_length=128, blank=True)
    
    def save(self, *args, **kwargs):
        """Sobrescribimos el método save para crear un checksum de verificación"""
        # Solo creamos checksum para pagos existentes
        if self.pk:
            # Crear un hash con datos críticos
            data_string = f"{self.referencia}:{self.pedido.id}:{self.monto}:{self.status}"
            salt = settings.SECRET_KEY[:16]  # Usamos parte de la clave secreta como sal
            
            # Creamos el hash
            self.checksum = hashlib.sha512((data_string + salt).encode('utf-8')).hexdigest()
            
            # Registrar cambio de estado si ha cambiado
            if self.pk and self._state.adding is False:
                try:
                    old_pago = Pago.objects.get(pk=self.pk)
                    if old_pago.status != self.status:
                        # Registrar el cambio en el historial
                        HistorialPago.objects.create(
                            pago=self,
                            estado_anterior=old_pago.status,
                            estado_nuevo=self.status
                        )
                        
                        # Registrar en log de seguridad si es completado o fallido
                        if self.status in ['completado', 'fallido', 'reembolsado']:
                            logger.info(f"Pago {self.referencia} cambió de {old_pago.status} a {self.status}")
                except Pago.DoesNotExist:
                    pass
                
        super().save(*args, **kwargs)
    
    def verify_integrity(self):
        """Verifica que el pago no ha sido manipulado comparando checksums"""
        data_string = f"{self.referencia}:{self.pedido.id}:{self.monto}:{self.status}"
        salt = settings.SECRET_KEY[:16]
        calculated_checksum = hashlib.sha512((data_string + salt).encode('utf-8')).hexdigest()
        
        # Devuelve True si coinciden, False si hay manipulación
        return calculated_checksum == self.checksum
    
    def __str__(self):
        return f"Pago {self.referencia} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

class HistorialPago(models.Model):
    """
    Registro de cambios de estado en los pagos para auditoría.
    """
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20, choices=Pago.STATUS_CHOICES)
    estado_nuevo = models.CharField(max_length=20, choices=Pago.STATUS_CHOICES)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    ip_usuario = models.GenericIPAddressField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.pago.referencia}: {self.estado_anterior} → {self.estado_nuevo}"
    
    class Meta:
        ordering = ['-fecha_cambio']