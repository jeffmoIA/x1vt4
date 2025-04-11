from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import render
import time
import logging
import re

logger = logging.getLogger('mototienda.security')

class LoginRateLimitMiddleware:
    """
    Middleware que previene ataques de fuerza bruta limitando los intentos de inicio de sesión.
    """
    def __init__(self, get_response):
        # Constructor que Django llamará cuando inicializa el middleware
        self.get_response = get_response
        
    def __call__(self, request):
        # Código que se ejecuta en cada solicitud antes de la vista
        
        # Solo aplicar restricciones a la página de inicio de sesión
        if request.path == '/usuarios/login/' and request.method == 'POST':
            # Obtener dirección IP del cliente
            ip_address = self._get_client_ip(request)
            
            # Clave única para esta IP en la caché
            cache_key = f'login_attempts_{ip_address}'
            
            # Obtener intentos anteriores o inicializar a cero
            login_attempts = cache.get(cache_key, 0)
            
            # Si hay demasiados intentos, bloquear
            if login_attempts >= 5:  # Máximo 5 intentos
                return render(request, 'usuarios/bloqueo_intentos.html', {
                    'tiempo_espera': 5,  # Minutos de bloqueo
                }, status=403)
            
            # Incrementar contador de intentos
            cache.set(cache_key, login_attempts + 1, 300)  # Expiración: 5 minutos
        
        # Llamar a la siguiente capa en la cadena de middlewares
        response = self.get_response(request)
        
        # Si el login es exitoso (redirección después del login), resetear contador
        if request.path == '/usuarios/login/' and request.method == 'POST' and response.status_code == 302:
            ip_address = self._get_client_ip(request)
            cache_key = f'login_attempts_{ip_address}'
            cache.delete(cache_key)  # Eliminar límite después de login exitoso
            
        return response
    
    def _get_client_ip(self, request):
        """Obtiene la dirección IP real del cliente, incluso detrás de proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Tomar la primera IP en caso de cadena de proxies
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
class SecurityHeadersMiddleware:
    """
    Middleware que añade cabeceras de seguridad a todas las respuestas
    para proteger contra varios ataques (XSS, Clickjacking, etc).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Añadir cabeceras de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (CSP) básico
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'",
            "img-src 'self' data: https://via.placeholder.com",
            "font-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self'",
            "frame-ancestors 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = "; ".join(csp_directives)
        
        return response
    
class SecurityAuditMiddleware:
    """
    Middleware que audita y registra patrones sospechosos en las solicitudes
    para detectar posibles ataques.
    """
    
    # Patrones de ataques comunes
    SUSPICIOUS_PATTERNS = [
        (r'(?i)(select|update|delete|insert|union|drop)\s+.*?\s*(from|table|where)', 'SQL Injection'),
        (r'(?i)<script[\s>]', 'XSS Attack'),
        (r'(?i)javascript:', 'XSS Attack'),
        (r'(?i)on(load|click|mouseover|submit|error)=', 'XSS Attack'),
        (r'(?i)/(etc|proc)/[a-z0-9]+', 'Path Traversal'),
        (r'(?i)\.\./', 'Path Traversal'),
        (r'(?i)cmd(\.exe)?|command(\.com)?', 'Command Injection'),
        (r'(?i)eval\(', 'Code Injection'),
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Verificar patrones sospechosos en la solicitud
        self._check_request(request)
        
        # Procesar la solicitud normalmente
        response = self.get_response(request)
        
        return response
    
    def _check_request(self, request):
        """Verifica si la solicitud contiene patrones sospechosos."""
        
        # Verificar URL
        self._check_content(request.path_info, 'URL', request)
        
        # Verificar parámetros GET
        for key, value in request.GET.items():
            self._check_content(value, f'GET param: {key}', request)
        
        # Verificar parámetros POST
        for key, value in request.POST.items():
            # Ignorar contraseñas en el log
            if 'password' not in key.lower():
                self._check_content(value, f'POST param: {key}', request)
        
        # Verificar cookies
        for key, value in request.COOKIES.items():
            if key not in ('sessionid', 'csrftoken'):  # Ignorar cookies sensibles
                self._check_content(value, f'Cookie: {key}', request)
    
    def _check_content(self, content, source, request):
        """Verifica si un contenido especifico coincide con patrones sospechosos."""
        if not isinstance(content, str):
            return
            
        for pattern, attack_type in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content):
                # Registrar incidente en el log
                logger.warning(
                    f"Possible {attack_type} detected! Source: {source}, IP: {self._get_client_ip(request)}, "
                    f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                    f"Path: {request.path}"
                )
                # Aquí podríamos tomar medidas adicionales como bloquear la solicitud
                break
    
    def _get_client_ip(self, request):
        """Obtiene la dirección IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip