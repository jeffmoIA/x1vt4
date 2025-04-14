from django.apps import AppConfig

class CarritoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carrito'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Aquí importamos los signals para que se registren.
        """
        import carrito.signals  # Importa los signals