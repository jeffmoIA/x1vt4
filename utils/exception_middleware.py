# utils/exception_middleware.py

import json
import traceback
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from utils.logger import log_exception

class GlobalExceptionMiddleware:
    """
    Middleware para capturar y manejar excepciones no controladas a nivel global.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Código que se ejecuta para cada solicitud antes de la vista
        return self.get_response(request)
        
    def process_exception(self, request, exception):
        """
        Procesa excepciones no controladas durante la solicitud.
        
        Args:
            request: Objeto HttpRequest
            exception: Excepción no controlada
            
        Returns:
            HttpResponse: Respuesta personalizada para el error
        """
        # Registrar la excepción
        context = {
            'url': request.path,
            'method': request.method,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        }
        log_exception(exception, context=context, notify=True)
        
        # Si es una solicitud AJAX, devolver una respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'Se ha producido un error. El equipo ha sido notificado.',
                'details': str(exception) if settings.DEBUG else None
            }, status=500)
            
        # Si es una solicitud normal y DEBUG está activado, dejar que Django maneje el error
        if settings.DEBUG:
            return None
            
        # En producción, mostrar una página de error personalizada
        try:
            context = {
                'error_message': 'Se ha producido un error inesperado.',
                'error_code': 500
            }
            html = render_to_string('errors/500.html', context, request)
            return HttpResponse(html, status=500)
        except:
            # Si hay algún error renderizando la plantilla, devolver una respuesta simple
            return HttpResponse(
                "Se ha producido un error inesperado. El equipo ha sido notificado.",
                status=500
            )