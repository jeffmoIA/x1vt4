from django.db import models
from django.contrib.auth.models import User
from catalogo.models import Producto

class Carrito(models.Model):
    # Modelo para representar el carrito de compras de un usuario
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario al que pertenece el carrito
    creado = models.DateTimeField(auto_now_add=True)  # Fecha de creación (automática)
    actualizado = models.DateTimeField(auto_now=True)  # Fecha de última actualización (automática)
    
    def __str__(self):
        # Representación en texto del carrito
        return f"Carrito de {self.usuario.username}"
    
    def total(self):
        # Método para calcular el total del carrito
        # Suma los subtotales de todos los items en el carrito
        return sum(item.subtotal() for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    # Campos para opciones del producto
    talla = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def subtotal(self):
        """Calcula el subtotal del item (precio * cantidad)"""
        from decimal import Decimal
        # Convertir a Decimal para garantizar precisión
        return Decimal(str(self.producto.precio)) * Decimal(str(self.cantidad))