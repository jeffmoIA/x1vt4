from django.apps import AppConfig

class CatalogoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogo'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Aquí importamos los signals para que se registren.
        """
        import catalogo.signals  # Importa los signals