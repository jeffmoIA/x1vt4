from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Vista para listar todos los productos
    path('productos/', views.lista_productos, name='lista_productos'),

    # Vista para mostrar detalles de un producto específico
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # Vista para listar productos por categoría
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),

    # Vista para listar productos por marca
    path('marca/<int:marca_id>/', views.productos_por_marca, name='productos_por_marca'),
]