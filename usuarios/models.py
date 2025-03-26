from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    # Relación uno a uno con el modelo User de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    # Campos adicionales
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    
