from django.urls import path
from . import views
from django.conf import settings
from django.http import HttpResponse

app_name = 'tienda'

# Primero define las URLs regulares
urlpatterns = [
    # Página principal
    path('', views.inicio, name='inicio'),
    # Página "Acerca de"
    path('acerca/', views.acerca, name='acerca'),
    # Página de contacto
    path('contacto/', views.contacto, name='contacto'),
]
# Luego añade URLs adicionales solo en modo debug
if settings.DEBUG:
    urlpatterns += [
        path('test-error/', views.test_error, name='test_error'),
    ]
