from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
     # Campo para el nombre de la categoría (motos, equipamiento, accesorios, etc.)
    nombre = models.CharField(max_length=100)

    # Descripción opcional de la categoría (puede quedar vacía)
    descripcion = models.TextField(blank=True, null=True)

    # Fecha en que se creó esta categoría (se llena automáticamente)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Método que define cómo se muestra la categoría en el admin y otros lugares
        return self.nombre

    class Meta:
        # Clase que permite configurar opciones adicionales del modelo
        verbose_name_plural = "Categorías"  # Nombre correcto en plural para el admin

class Marca(models.Model):
    # Nombre de la marca (Honda, Yamaha, Alpinestars, etc.)
    nombre = models.CharField(max_length=100)

    # Información adicional sobre la marca
    descripcion = models.TextField(blank=True, null=True)

    # Imagen del logo de la marca (se guardará en la carpeta 'marcas/')
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)

    def __str__(self):
        # Representación textual de la marca
        return self.nombre

class Producto(models.Model):
    # Información básica del producto
    nombre = models.CharField(max_length=200) # Nombre del producto
    descripcion = models.TextField() # Descripción del producto

    # Precio con 2 decimales y hasta 10 dígitos en total (incluidos decimales)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

     # Relación con otros modelos:
    # - ForeignKey crea una relación uno-a-muchos (una categoría puede tener muchos productos)
    # - on_delete=models.CASCADE significa que si se elimina una categoría, se eliminan todos sus productos
    # - related_name permite acceder a los productos desde la categoría usando categoria.productos.all()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')

     # Relación con la marca del producto
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='productos')

     # Información de inventario
    stock = models.PositiveIntegerField(default=0) # Cantidad de productos disponibles
    disponible = models.BooleanField(default=True) # Indica si el producto está disponible
     
     # Fecha en que se añadió el producto al catálogo
    fecha_creacion = models.DateTimeField(auto_now_add=True)

     # Imagen principal del producto (se guardará en la carpeta 'productos/')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        # Representación textual del producto
        return self.nombre
    
# En catalogo/models.py, añade este nuevo modelo
class TallaProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='tallas')
    talla = models.CharField(max_length=20)  # Puede ser "S", "M", "42", "54", etc.
    disponible = models.BooleanField(default=True)  # Indica si esta talla está disponible
    stock = models.PositiveIntegerField(default=0)  # Stock para esta talla específica

    class Meta:
        # Asegura que no pueda haber duplicados de talla para un mismo producto
        unique_together = ('producto', 'talla')
        verbose_name = "Talla de producto"
        verbose_name_plural = "Tallas de productos"

    def __str__(self):
        return f"{self.producto.nombre} - Talla {self.talla}"

# Añadir el nuevo modelo para imágenes múltiples
class ImagenProducto(models.Model):
    # Relación con el producto (muchas imágenes pueden pertenecer a un producto)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    
    # Campo para la imagen
    imagen = models.ImageField(upload_to='productos/imagenes/')
    
    # Orden de visualización de la imagen
    orden = models.PositiveIntegerField(default=1)
    
    # Indicar si es la imagen principal
    es_principal = models.BooleanField(default=False)
    
    # Título opcional para la imagen (SEO)
    titulo = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        ordering = ['orden']  # Ordenar por el campo 'orden'
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"
    
    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        # Si esta imagen se marca como principal, quitar el flag de las demás
        if self.es_principal:
            ImagenProducto.objects.filter(
                producto=self.producto, 
                es_principal=True
            ).exclude(id=self.id or 0).update(es_principal=False)
        
        # Si no hay imágenes para este producto o no hay ninguna principal,
        # marcar esta como principal automáticamente
        elif not self.id:  # Si es un objeto nuevo
            if not ImagenProducto.objects.filter(producto=self.producto).exists() or \
               not ImagenProducto.objects.filter(producto=self.producto, es_principal=True).exists():
                self.es_principal = True
        
        super().save(*args, **kwargs)
        
class ImagenProducto(models.Model):
    # Relación con el producto (un producto puede tener muchas imágenes)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    
    # Campo para almacenar la imagen
    imagen = models.ImageField(upload_to='productos/imagenes/')
    
    # Campo para ordenar las imágenes (útil para determinar la imagen principal)
    orden = models.PositiveIntegerField(default=0)
    
    # Campo para marcar una imagen como principal
    es_principal = models.BooleanField(default=False)
    
    # Campo para añadir un título a la imagen
    titulo = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        ordering = ['orden']  # Ordenar imágenes por el campo 'orden'
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"
    
    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"