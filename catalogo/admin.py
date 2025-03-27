from django.contrib import admin
from .models import Categoria, Marca, Producto, TallaProducto

# Registra el modelo Categoria en el panel de administración
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista de categorías
    list_display = ('nombre', 'fecha_creacion')
    # Campos por los que se puede buscar
    search_fields = ('nombre',)

# Registra el modelo Marca en el panel de administración
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class TallaProductoInline(admin.TabularInline):
    model = TallaProducto
    extra = 1  # Número de formularios vacíos a mostrar

# Registra el modelo Producto en el panel de administración
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas en la lista de productos
    list_display = ('nombre', 'precio', 'categoria', 'marca', 'stock', 'disponible')
    # Campos de búsqueda
    search_fields = ('nombre', 'descripcion')
    # Filtros laterales
    list_filter = ('categoria', 'marca', 'disponible')
    # Ordenar por fecha de creación (más reciente primero)
    inlines = [TallaProductoInline]  # Añade la gestión de tallas integrada
    ordering = ('-fecha_creacion',)