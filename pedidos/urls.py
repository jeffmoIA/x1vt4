from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('mis-pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    path('pedido/<int:pedido_id>/factura/', views.obtener_factura, name='factura_pedido'),
    # Nueva URL para estadísticas de pedidos (solo administradores)
    path('admin/estadisticas/', views.estadisticas_pedidos, name='estadisticas_pedidos'),
    path('admin/pedidos/', views.admin_lista_pedidos, name='admin_lista_pedidos'),
    path('admin/pedido/<int:pedido_id>/cambiar-estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('admin/pedido/<int:pedido_id>/', views.admin_detalle_pedido, name='admin_detalle_pedido'),
    path('admin/pedido/<int:pedido_id>/actualizar-seguimiento/', views.actualizar_seguimiento, name='actualizar_seguimiento'),
    path('admin/pedidos/exportar/excel/', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),
    path('admin/pedido/<int:pedido_id>/cambiar-estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
]