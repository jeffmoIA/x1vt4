from django.core import management

# Forzar el descubrimiento de comandos en este directorio
path = __path__[0]
management.find_commands(path)