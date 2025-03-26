from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('mis-pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
]