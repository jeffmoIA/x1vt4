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
    path('admin/productos/', views.admin_lista_productos, name='admin_lista_productos'),
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),
    path('admin/productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('admin/productos/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

]