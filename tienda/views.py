from django.conf import settings
from django.shortcuts import render
from catalogo.models import Categoria, Producto
from utils.logger import log_exception, log_audit

def test_error(request):
    """
    Vista de prueba para generar errores y verificar el sistema de logging.
    Solo disponible en modo DEBUG.
    """
    if not settings.DEBUG:
        raise Http404("Esta página solo está disponible en modo desarrollo")
    
    error_type = request.GET.get('type', 'exception')
    
    if error_type == '404':
        raise Http404("Esta es una prueba de error 404")
    elif error_type == '403':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Esta es una prueba de error 403")
    elif error_type == '500':
        # Registrar un error de prueba
        try:
            raise ValueError("Esta es una prueba de error 500")
        except ValueError as e:
            # Si ya has implementado log_exception, descomenta estas líneas:
            # from utils.logger import log_exception
            # log_exception(e, context={'test': True, 'user': request.user.username})
            raise
    elif error_type == 'sentry':
        # Prueba específica para Sentry
        try:
            # Provocar un error deliberadamente
            division_por_cero = 1 / 0
        except Exception as e:
            # Capturar y enviar el error a Sentry
            import sentry_sdk
            sentry_sdk.capture_exception(e)
            return HttpResponse("Error enviado a Sentry. Verifica tu panel de Sentry.")
    else:
        # Error genérico
        raise Exception("Esta es una prueba de error no controlado")
    

def inicio(request):
    """Obtiene productos recientes y categorías para mostrar en la página principal."""
    # Obtener los productos más recientes para mostrar en la página principal
    productos_recientes = Producto.objects.filter(disponible=True).order_by('-id')[:6]
    
    # Obtener todas las categorías para el menú de navegación
    categorias = Categoria.objects.all()
    
    return render(request, 'tienda/inicio.html', {
        'productos_recientes': productos_recientes,
        'categorias': categorias
    })

def acerca(request):
    """Vista para la página 'Acerca de'."""
    return render(request, 'tienda/acerca.html')

def contacto(request):
    """Vista para la página de contacto."""
    return render(request, 'tienda/contacto.html')