from django.urls import path
from . import views

app_name = 'carrito'  # Namespace para las URL del carrito

urlpatterns = [
    # Ruta para ver el contenido del carrito
    path('', views.ver_carrito, name='ver_carrito'),
    
    # Ruta para añadir un producto al carrito (requiere ID del producto)
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    
    # Ruta para actualizar la cantidad de un producto (requiere ID del item)
    path('actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    
    # Ruta para eliminar un producto del carrito (requiere ID del item)
    path('eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
]