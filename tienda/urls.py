from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    # Página principal
    path('', views.inicio, name='inicio'),
    
    # Página "Acerca de"
    path('acerca/', views.acerca, name='acerca'),
    
    # Página de contacto
    path('contacto/', views.contacto, name='contacto'),
]