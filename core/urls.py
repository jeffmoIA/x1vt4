"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL para el panel de administración
    path('admin/', admin.site.urls),
    # URLs de la aplicación catálogo
    path('catalogo/', include('catalogo.urls')),
    # URLs de la aplicación usuarios
    path('usuarios/', include('usuarios.urls')),
    # URLs de la aplicación carrito
    path('carrito/', include('carrito.urls')),
    # URLs de la aplicación pedidos
    path('pedidos/', include('pedidos.urls')),
    # URL para la página principal (root)
    path('', include('tienda.urls')),
    
    
]

# Configuración para servir archivos de medios durante desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
     # Añadir URLs para Django Debug Toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]