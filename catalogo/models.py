from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Adjust
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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
    
@receiver(post_save, sender=Categoria)
def categoria_saved(sender, instance, created, **kwargs):
        """Invalidar caché cuando se guarda una categoría"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('categoria', instance.id)
        
@receiver(post_delete, sender=Categoria)
def categoria_deleted(sender, instance, **kwargs):
        """Invalidar caché cuando se elimina una categoría"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('categoria', instance.id)

class Marca(models.Model):
    # Nombre de la marca (Honda, Yamaha, Alpinestars, etc.)
    nombre = models.CharField(max_length=100)

    # Información adicional sobre la marca
    descripcion = models.TextField(blank=True, null=True)

    # Imagen del logo de la marca (se guardará en la carpeta 'marcas/')
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)

    def __str__(self):
        return self.nombre
        
    def save(self, *args, **kwargs):
        # Normalizar el nombre antes de guardar
        self.nombre = self.nombre.strip()
        super().save(*args, **kwargs)
    
@receiver(post_save, sender=Marca)
def marca_saved(sender, instance, created, **kwargs):
        """Invalidar caché cuando se guarda una marca"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('marca', instance.id)
        
@receiver(post_delete, sender=Marca)
def marca_deleted(sender, instance, **kwargs):
        """Invalidar caché cuando se elimina una marca"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('marca', instance.id)

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
    
    def get_thumbnail_url(self):
        """
        Devuelve la URL de la miniatura para la tabla, con un timestamp anti-caché.
        """
        import time
        timestamp = int(time.time())
        
        # Intentar obtener la miniatura desde la imagen principal
        principal = self.get_imagen_principal()
        if principal and hasattr(principal, 'thumbnail_tabla'):
            try:
                # Generar la URL con acceso a través de .url para verificar que exista
                return f"{principal.thumbnail_tabla.url}?v={timestamp}"
            except Exception:
                pass  # Si hay error, seguir con el siguiente método
                
        # Si no hay miniatura específica, intentar con la imagen normal
        if principal and principal.imagen:
            return f"{principal.imagen.url}?v={timestamp}"
            
        # Si no hay imagen principal pero hay imagen en el producto
        if self.imagen:
            return f"{self.imagen.url}?v={timestamp}"
        
        # Si no hay nada, devolver un placeholder
        return "/static/img/placeholder.png"

    def __str__(self):
        # Representación textual del producto
        return self.nombre
    
@receiver(post_save, sender=Producto)
def producto_saved(sender, instance, created, **kwargs):
        """Invalidar caché cuando se guarda un producto"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('producto', instance.id)
        
@receiver(post_delete, sender=Producto)
def producto_deleted(sender, instance, **kwargs):
        """Invalidar caché cuando se elimina un producto"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('producto', instance.id)
        
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
    
@receiver(post_save, sender=TallaProducto)
def talla_producto_saved(sender, instance, created, **kwargs):
        """Invalidar caché de producto cuando se guarda una talla"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('producto', instance.producto.id)
        
@receiver(post_delete, sender=TallaProducto)
def talla_producto_deleted(sender, instance, **kwargs):
        """Invalidar caché de producto cuando se elimina una talla"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('producto', instance.producto.id)


def validate_image_size(image):
    """
    Valida que el tamaño de la imagen no exceda 5MB
    """
    # Limitar el tamaño de la imagen a 5MB
    max_size = 5 * 1024 * 1024  # 5MB en bytes
    # Verificar que la imagen tiene un tamaño
    if hasattr(image, 'size') and image.size > max_size:
        raise ValidationError(f'La imagen es demasiado grande. El tamaño máximo permitido es 5MB.')


class ImagenProducto(models.Model):
    # Relación con el producto
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    
    # Campo para la imagen
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
    # Miniatura específica para DataTable (más pequeña y optimizada)
    thumbnail_tabla = ImageSpecField(
        source='imagen',
        processors=[
            ResizeToFill(80, 80),  # Tamaño pequeño ideal para tablas
            Adjust(sharpness=1.2),  # Aumentar nitidez para compensar el tamaño reducido
        ],
        format='JPEG',
        options={'quality': 70}  # Calidad menor para reducir el tamaño
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
        # Eliminamos la constraint para evitar errores al guardar imágenes con el mismo orden
    
    def __str__(self):
        """Representación legible del objeto"""
        principal_str = " (Principal)" if self.es_principal else ""
        return f"Imagen {self.orden}{principal_str} de {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        """Método personalizado para guardar"""
        # Si esta imagen se marca como principal, quitar el flag de las demás
        if self.es_principal and self.producto_id:  # Asegurar que tenemos producto
            ImagenProducto.objects.filter(
                producto=self.producto, 
                es_principal=True
            ).exclude(id=self.id or 0).update(es_principal=False)
        
        # Si es la primera imagen, marcarla como principal
        elif not self.id and not ImagenProducto.objects.filter(producto=self.producto).exists():
            self.es_principal = True
            
        # Si no hay ninguna imagen principal, marcar esta como principal
        elif not ImagenProducto.objects.filter(producto=self.producto, es_principal=True).exists():
            self.es_principal = True
        
        # Controlar que no haya más de 10 imágenes por producto
        if not self.id and ImagenProducto.objects.filter(producto=self.producto).count() >= 10:
            raise ValidationError("No se pueden añadir más de 10 imágenes por producto.")
        
        # Guardar normalmente
        super().save(*args, **kwargs)
    
    def get_thumbnail_url(self):
        """Método auxiliar para obtener la URL de la miniatura"""
        return self.thumbnail.url if hasattr(self, 'thumbnail') else self.imagen.url
    
    def get_carrusel_url(self):
        """Método auxiliar para obtener la URL de la imagen de carrusel"""
        return self.carrusel.url if hasattr(self, 'carrusel') else self.imagen.url
    
@receiver(post_save, sender=ImagenProducto)
def imagen_producto_saved(sender, instance, created, **kwargs):
        """Invalidar caché de producto cuando se guarda una imagen"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('producto', instance.producto.id)
        
@receiver(post_delete, sender=ImagenProducto)
def imagen_producto_deleted(sender, instance, **kwargs):
        """Invalidar caché de producto cuando se elimina una imagen"""
        from utils.cache_utils import invalidate_model_cache
        invalidate_model_cache('producto', instance.producto.id)

