from django.db import models

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
        verbose_nombre_plural = "Categorías"  # Nombre correcto en plural para el admin

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
    # - related_nombre permite acceder a los productos desde la categoría usando categoria.productos.all()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_nombre='productos')

     # Relación con la marca del producto
    logo = models.ForeignKey(Marca, on_delete=models.CASCADE, related_nombre='productos')

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