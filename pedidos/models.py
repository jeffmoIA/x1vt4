from django.db import models
from django.contrib.auth.models import User
from catalogo.models import Producto

class Pedido(models.Model):
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
    pagado = models.BooleanField(default=False)
    
    # Estado del pedido (pendiente, procesando, enviado, entregado, cancelado)
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    
    # Notas adicionales
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f'Pedido {self.id} - {self.usuario.username}'
    
    def total(self):
        """Calcula el total del pedido sumando todos los ítems"""
        return sum(item.precio_total() for item in self.items.all())

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