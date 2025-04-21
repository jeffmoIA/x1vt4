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
    
    # Vistas de administración
    path('admin/productos/', views.admin_lista_productos, name='admin_lista_productos'),
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),
    path('admin/productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('admin/productos/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    # Ruta para procesar solicitudes AJAX de DataTables
    path('admin/productos/data/', views.admin_productos_data, name='admin_productos_data'),
    path('admin/marcas/listar/', views.listar_marcas_ajax, name='listar_marcas_ajax'),
    path('admin/marcas/', views.gestionar_marcas, name='gestionar_marcas'),
    path('api/marcas/', views.obtener_marcas_json, name='obtener_marcas_json'),
    # Añade estas nuevas rutas:
    path('admin/marcas/crear/', views.crear_marca, name='crear_marca'), 
    path('admin/marcas/editar/', views.editar_marca, name='editar_marca'),  
    path('admin/marcas/eliminar/', views.eliminar_marca, name='eliminar_marca'),  
    path('admin/marcas/gestionar/', views.gestionar_marcas, name='gestionar_marcas_standalone'),
    # Vista para productos populares (cacheada)
    path('populares/', views.productos_populares, name='productos_populares'),
   
    
]