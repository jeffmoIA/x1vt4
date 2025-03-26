from django.db import models

class Categoria(models.Model):
     # Campo para el nombre de la categoría (motos, equipamiento, accesorios, etc.)
    name = models.CharField(max_length=100)

    # Descripción opcional de la categoría (puede quedar vacía)
    description = models.TextField(blank=True, null=True)

    # Fecha en que se creó esta categoría (se llena automáticamente)
    date_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Método que define cómo se muestra la categoría en el admin y otros lugares
        return self.name

    class Meta:
        # Clase que permite configurar opciones adicionales del modelo
        verbose_name_plural = "Categorías"  # Nombre correcto en plural para el admin

class Marca(models.Model):
    # Nombre de la marca (Honda, Yamaha, Alpinestars, etc.)
    name = models.CharField(max_length=100)

    # Información adicional sobre la marca
    description = models.TextField(blank=True, null=True)

    # Imagen del logo de la marca (se guardará en la carpeta 'marcas/')
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)

    def __str__(self):
        # Representación textual de la marca
        return self.name

class Producto(models.Model):
    # Información básica del producto
    name = models.CharField(max_length=200) # Nombre del producto
    description = models.TextField() # Descripción del producto

    # Precio con 2 decimales y hasta 10 dígitos en total (incluidos decimales)
    price = models.DecimalField(max_digits=10, decimal_places=2)

     # Relación con otros modelos:
    # - ForeignKey crea una relación uno-a-muchos (una categoría puede tener muchos productos)
    # - on_delete=models.CASCADE significa que si se elimina una categoría, se eliminan todos sus productos
    # - related_name permite acceder a los productos desde la categoría usando categoria.productos.all()
    category = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')

     # Relación con la marca del producto
    brand = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='productos')

     # Información de inventario
    stock = models.PositiveIntegerField(default=0) # Cantidad de productos disponibles
    available = models.BooleanField(default=True) # Indica si el producto está disponible
     
     # Fecha en que se añadió el producto al catálogo
    date_create = models.DateTimeField(auto_now_add=True)

     # Imagen principal del producto (se guardará en la carpeta 'productos/')
    image = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        # Representación textual del producto
        return self.name