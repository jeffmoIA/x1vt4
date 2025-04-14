from django.apps import AppConfig

class PedidosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedidos'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Aquí importamos los signals para que se registren.
        """
        import pedidos.signals  # Importa los signals