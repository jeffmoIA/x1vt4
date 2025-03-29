from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Adjust
from django.utils import timezone

def get_default_date():
    """Función que devuelve la fecha y hora actual como valor predeterminado"""
    return timezone.now()
    
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
    
    def get_imagen_principal(self):
        """
        Devuelve la imagen principal del producto, o la primera imagen,
        o None si no hay imágenes.
        """
        # Primero intentar obtener la imagen marcada como principal
        principal = self.imagenes.filter(es_principal=True).first()
        if principal:
            return principal
            
        # Si no hay imagen principal, devolver la primera imagen
        return self.imagenes.first() or None
        
    def get_imagen_url(self):
        """
        Devuelve la URL de la imagen principal con un timestamp para evitar caché.
        """
        import time
        timestamp = int(time.time())
        
        # Primero intentar con las imágenes nuevas
        principal = self.get_imagen_principal()
        if principal and principal.imagen:
            return f"{principal.imagen.url}?v={timestamp}"
            
        # Luego intentar con la imagen original
        if self.imagen:
            return f"{self.imagen.url}?v={timestamp}"
            
        # Si no hay imágenes, devolver un placeholder
        return "https://via.placeholder.com/300x200?text=Sin+imagen"

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


def validate_image_size(image):
    """
    Valida que el tamaño de la imagen no exceda 5MB
    """
    # Limitar el tamaño de la imagen a 5MB
    max_size = 5 * 1024 * 1024  # 5MB en bytes
    if image.size > max_size:
        raise ValidationError(f'La imagen es demasiado grande. El tamaño máximo permitido es 5MB.')

class ImagenProducto(models.Model):
    # Relación con el producto
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    
    # Campo para la imagen principal procesada automáticamente
    imagen = ProcessedImageField(
        upload_to='productos/imagenes/',
        processors=[
            ResizeToFit(1200, 1200),  # Redimensiona manteniendo la proporción
            Adjust(contrast=1.1, sharpness=1.1),  # Mejora ligeramente el contraste y nitidez
        ],
        format='JPEG',
        options={'quality': 85},  # Calidad de compresión (85% es un buen balance)
        validators=[validate_image_size],
        help_text="Tamaño máximo: 5MB. Se redimensionará automáticamente."
    )
    
    # Miniatura para listados de productos (generada automáticamente)
    thumbnail = ImageSpecField(
        source='imagen',
        processors=[
            ResizeToFill(300, 300),  # Recorta para llenar exactamente 300x300px
            Adjust(brightness=1.05),  # Ligeramente más brillante para miniaturas
        ],
        format='JPEG',
        options={'quality': 75}  # Menor calidad para miniaturas (ahorra espacio)
    )
    
    # Versión optimizada para el carrusel
    carrusel = ImageSpecField(
        source='imagen',
        processors=[
            ResizeToFit(800, 600),  # Tamaño ideal para el carrusel
        ],
        format='JPEG',
        options={'quality': 80}
    )
    
    # Versión pequeña para las miniaturas de navegación
    miniatura_nav = ImageSpecField(
        source='imagen',
        processors=[
            ResizeToFill(100, 100),  # Tamaño fijo para navegación uniforme
        ],
        format='JPEG',
        options={'quality': 70}
    )
    
    # Orden de visualización de la imagen
    orden = models.PositiveIntegerField(
        default=0, 
        help_text="Orden de aparición en la galería (menor número = aparece primero)"
    )
    
    # Indicador de imagen principal
    es_principal = models.BooleanField(
        default=False, 
        help_text="Marcar como imagen principal del producto"
    )
    
    # Título para SEO y accesibilidad
    titulo = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Título descriptivo para SEO y accesibilidad"
    )
    
    # Campos de metadatos para administración
    fecha_creacion = models.DateTimeField(
    auto_now_add=True,
    help_text="Fecha de creación de la imagen"
    )   
    ultima_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden', '-es_principal']  # Ordenar primero por orden, luego principal
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"
        constraints = [
            # Limitar a 10 imágenes por producto a nivel de base de datos
            models.UniqueConstraint(
                fields=['producto', 'orden'],
                name='unique_product_image_order'
            ),
        ]
    
    def __str__(self):
        """Representación legible del objeto"""
        principal_str = " (Principal)" if self.es_principal else ""
        return f"Imagen {self.orden}{principal_str} de {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        """Método personalizado para guardar, con lógica para imagen principal"""
        # Si esta imagen se marca como principal, quitar el flag de las demás
        if self.es_principal:
            ImagenProducto.objects.filter(
                producto=self.producto, 
                es_principal=True
            ).exclude(id=self.id or 0).update(es_principal=False)
        
        # Si es la primera imagen para el producto, marcarla como principal
        elif not self.id and not ImagenProducto.objects.filter(producto=self.producto).exists():
            self.es_principal = True
            
        # Si no hay ninguna imagen principal, marcar esta como principal
        elif not ImagenProducto.objects.filter(producto=self.producto, es_principal=True).exists():
            self.es_principal = True
        
        # Controlar que no haya más de 10 imágenes por producto
        if not self.id and ImagenProducto.objects.filter(producto=self.producto).count() >= 10:
            raise ValidationError("No se pueden añadir más de 10 imágenes por producto.")
        
        super().save(*args, **kwargs)
    
    def get_thumbnail_url(self):
        """Método auxiliar para obtener la URL de la miniatura"""
        return self.thumbnail.url if hasattr(self, 'thumbnail') else self.imagen.url
    
    def get_carrusel_url(self):
        """Método auxiliar para obtener la URL de la imagen de carrusel"""
        return self.carrusel.url if hasattr(self, 'carrusel') else self.imagen.url