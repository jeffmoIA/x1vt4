import time
import threading
import logging
import psutil
import os
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

# Configuración del logger
logger = logging.getLogger('mototienda.performance')

class PerformanceMonitorMiddleware(MiddlewareMixin):
    """
    Middleware que monitorea el rendimiento de las peticiones HTTP.
    Registra tiempo de respuesta, uso de CPU y memoria, y consultas SQL.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.process = psutil.Process(os.getpid())
        self._local = threading.local()
        
    def process_request(self, request):
        """Registra el tiempo de inicio de la petición"""
        self._local.start_time = time.time()
        self._local.start_cpu = self.process.cpu_percent()
        self._local.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self._local.num_queries_start = len(connection.queries)
    
    def process_response(self, request, response):
        """
        Registra métricas de rendimiento al finalizar la petición
        """
        # Saltamos rutas de archivos estáticos y admin para no saturar los logs
        path = request.path
        if path.startswith('/static/') or path.startswith('/media/') or path.startswith('/admin/jsi18n/'):
            return response
        
        # Calculamos las métricas de rendimiento
        try:
            # Tiempo de respuesta
            total_time = time.time() - self._local.start_time
            
            # Uso de CPU
            end_cpu = self.process.cpu_percent()
            cpu_usage = end_cpu - self._local.start_cpu if end_cpu > self._local.start_cpu else 0
            
            # Uso de memoria
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = end_memory - self._local.start_memory
            
            # Número de consultas SQL
            queries_executed = len(connection.queries) - self._local.num_queries_start
            
            # Registrar peticiones lentas (más de 500ms)
            if total_time > 0.5:  # 500ms
                logger.warning(
                    f"Petición lenta: {request.method} {path} - "
                    f"Tiempo: {total_time:.2f}s, "
                    f"CPU: {cpu_usage:.1f}%, "
                    f"Memoria: {memory_diff:.2f}MB, "
                    f"Consultas: {queries_executed}"
                )
                
                # Para peticiones muy lentas (más de 1s), registramos las consultas
                if total_time > 1.0 and queries_executed > 10:
                    for i, query in enumerate(connection.queries[-queries_executed:]):
                        logger.warning(f"  Consulta {i+1}: {query['sql'][:200]}... "
                                      f"({float(query['time']):.3f}s)")
            
            # Añadir headers de rendimiento para depuración
            response['X-Time-Taken'] = f"{total_time:.3f}s"
            response['X-Queries-Count'] = str(queries_executed)
            
        except Exception as e:
            # No fallamos si hay errores en el monitoreo
            logger.error(f"Error en monitoreo de rendimiento: {str(e)}")
        
        return response