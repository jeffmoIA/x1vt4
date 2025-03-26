from django.contrib import admin
from .models import Categoria, Marca, Producto

# Registra el modelo Categoria en el panel de administración
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista de categorías
    list_display = ('name', 'date_create')
    # Campos por los que se puede buscar
    search_fields = ('name',)

# Registra el modelo Marca en el panel de administración
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Registra el modelo Producto en el panel de administración
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas en la lista de productos
    list_display = ('name', 'price', 'category', 'brand', 'stock', 'available')
    # Campos de búsqueda
    search_fields = ('name', 'description')
    # Filtros laterales
    list_filter = ('category', 'brand', 'available')
    # Ordenar por fecha de creación (más reciente primero)
    ordering = ('-date_create',)