from django.apps import AppConfig

class PagosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pagos'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Registra las señales para monitoreo de seguridad.
        """
        import pagos.signals  # Importar señales
