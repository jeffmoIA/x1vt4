from django.db import models
from django.contrib.auth.models import User
from catalogo.models import Producto
from django.utils import timezone

class Pedido(models.Model):
    # Estados del pedido
    PENDIENTE = 'pendiente'
    PROCESANDO = 'procesando'
    ENVIADO = 'enviado'
    ENTREGADO = 'entregado'
    CANCELADO = 'cancelado'
    
    ESTADOS = (
        (PENDIENTE, 'Pendiente'),
        (PROCESANDO, 'Procesando'),
        (ENVIADO, 'Enviado'),
        (ENTREGADO, 'Entregado'),
        (CANCELADO, 'Cancelado'),
    )
    
    # Usuario que realizó el pedido
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    
    # Información de envío
    nombre_completo = models.CharField(max_length=100)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    
    # Información del pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    pagado = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=50, blank=True)
    referencia_pago = models.CharField(max_length=100, blank=True)
    
    # Estado del pedido
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    
    # Seguimiento
    codigo_seguimiento = models.CharField(max_length=100, blank=True)
    empresa_envio = models.CharField(max_length=100, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    # Notas adicionales
    notas = models.TextField(blank=True, null=True)
    notas_admin = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f'Pedido {self.id} - {self.usuario.username}'
    
    def total(self):
        """Calcula el total del pedido sumando todos los ítems"""
        return sum(item.precio_total() for item in self.items.all())
    
    def cambiar_estado(self, nuevo_estado, notas=None):
        """Cambiar el estado del pedido y guardar registro del cambio"""
        if nuevo_estado in dict(self.ESTADOS).keys():
            estado_anterior = self.estado
            self.estado = nuevo_estado
            
            # Actualizar fechas de seguimiento según el estado
            if nuevo_estado == self.ENVIADO and not self.fecha_envio:
                self.fecha_envio = timezone.now()
            elif nuevo_estado == self.ENTREGADO and not self.fecha_entrega:
                self.fecha_entrega = timezone.now()
            
            self.save()
            
            # Registrar el cambio de estado
            HistorialEstadoPedido.objects.create(
                pedido=self,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                notas=notas
            )
            
            return True
        return False

class HistorialEstadoPedido(models.Model):
    """Modelo para registrar cambios de estado en pedidos"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20, choices=Pedido.ESTADOS)
    estado_nuevo = models.CharField(max_length=20, choices=Pedido.ESTADOS)
    notas = models.TextField(blank=True, null=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.pedido.id}: {self.estado_anterior} → {self.estado_nuevo}"

class ItemPedido(models.Model):
    # Relación con el pedido
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    
    # Relación con el producto
    producto = models.ForeignKey(Producto, related_name='items_pedido', on_delete=models.CASCADE)
    
    # Precio al momento de la compra (puede cambiar en el futuro)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Cantidad de unidades
    cantidad = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.id}'
    
    def precio_total(self):
        """Calcula el subtotal de este ítem (precio * cantidad)"""
        return self.precio * self.cantidad