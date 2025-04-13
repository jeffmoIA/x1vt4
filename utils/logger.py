# utils/logger.py

import logging
import traceback
import time
import functools
import json
import os
from datetime import datetime
from django.conf import settings
from django.core.mail import mail_admins

# Configurar loggers básicos

# Logger principal de la aplicación
logger = logging.getLogger('mototienda')
# Logger específico para errores
error_logger = logging.getLogger('mototienda.error')  
 # Logger para eventos de seguridad
security_logger = logging.getLogger('mototienda.security')
 # Logger para métricas de rendimiento 
performance_logger = logging.getLogger('mototienda.performance') 
# Logger para auditoría de acciones
audit_logger = logging.getLogger('mototienda.audit')  

def log_exception(exc, context=None, notify=True):
    """
    Registra una excepción y opcionalmente envía una notificación por email.
    
    Args:
        exc: La excepción capturada
        context: Diccionario con contexto adicional
        notify: Booleano para indicar si debe notificar por email
    """
    # Crear un diccionario con información detallada sobre la excepción
    error_details = {
        'exception_type': exc.__class__.__name__,
        'exception_message': str(exc),
        'traceback': traceback.format_exc(),
        'timestamp': datetime.now().isoformat(),
        'context': context or {}
    }
    
    # Registrar el error en el log con nivel ERROR
    error_logger.error(
        f"Exception: {exc.__class__.__name__} - {str(exc)}",
        extra={'error_details': json.dumps(error_details)}
    )
    
    # Enviar email a los administradores si está configurado y se solicita
    if notify and hasattr(settings, 'ADMINS') and settings.ADMINS:
        subject = f'Error en MotoTienda: {exc.__class__.__name__}'
        message = (
            f"Se ha producido el siguiente error:\n\n"
            f"Tipo: {exc.__class__.__name__}\n"
            f"Mensaje: {str(exc)}\n\n"
            f"Traceback:\n{traceback.format_exc()}\n\n"
            f"Contexto adicional:\n{json.dumps(context or {}, indent=2)}"
        )
        mail_admins(subject, message, fail_silently=True)

def log_security_event(event_type, details, level='INFO'):
    """
    Registra un evento de seguridad.
    
    Args:
        event_type: Tipo de evento (auth_success, auth_failure, permission_denied, etc)
        details: Detalles del evento
        level: Nivel de log (INFO, WARNING, ERROR, CRITICAL)
    """
    log_method = getattr(security_logger, level.lower())
    log_method(f"Security event: {event_type}", extra={'details': details})

def log_performance(operation, execution_time, metadata=None):
    """
    Registra métricas de rendimiento.
    
    Args:
        operation: Nombre de la operación monitoreada
        execution_time: Tiempo de ejecución en segundos
        metadata: Información adicional sobre la operación
    """
    metadata = metadata or {}
    performance_logger.info(
        f"Performance: {operation} took {execution_time:.4f}s",
        extra={
            'operation': operation,
            'execution_time': execution_time,
            'metadata': metadata
        }
    )

def log_audit(user, action, object_type=None, object_id=None, details=None):
    """
    Registra acciones de usuario para auditoría.
    
    Args:
        user: Usuario que realiza la acción
        action: Acción realizada (create, update, delete, view)
        object_type: Tipo de objeto afectado
        object_id: ID del objeto afectado
        details: Detalles adicionales
    """
    username = user.username if hasattr(user, 'username') else str(user)
    audit_logger.info(
        f"AUDIT: {username} - {action}",
        extra={
            'user': username,
            'action': action,
            'object_type': object_type,
            'object_id': object_id,
            'details': details or {}
        }
    )

def performance_monitor(name=None):
    """
    Decorador para monitorear el rendimiento de una función.
    
    Args:
        name: Nombre personalizado para la operación
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            operation_name = name or func.__name__
            log_performance(operation_name, execution_time)
            
            return result
        return wrapper
    return decorator

def exception_handler(notify=True):
    """
    Decorador para manejar excepciones en una función.
    
    Args:
        notify: Booleano para indicar si debe notificar por email
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Obtener información de contexto
                context = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                log_exception(e, context, notify=notify)
                # Re-lanzar la excepción para que sea manejada arriba
                raise
        return wrapper
    return decorator