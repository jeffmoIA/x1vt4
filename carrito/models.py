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
    # Modelo para representar cada producto en el carrito
    # Relación con el carrito, related_name permite acceder a items desde carrito.items.all()
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Producto añadido
    cantidad = models.PositiveIntegerField(default=1)  # Cantidad del producto (siempre positiva)
    
    def __str__(self):
        # Representación en texto del item
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def subtotal(self):
        # Método para calcular el subtotal (precio * cantidad)
        return self.producto.precio * self.cantidad