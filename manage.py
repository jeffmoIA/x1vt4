#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
import dotenv  # Importamos dotenv para cargar variables de entorno

def main():
    """Run administrative tasks."""
    # Cargar variables de entorno
    dotenv_path = Path(__file__).resolve().parent / '.env'
    if dotenv_path.exists():
        dotenv.load_dotenv(str(dotenv_path))
        print("Variables de entorno cargadas desde .env")

    # Configurar el módulo de settings por defecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')  # Por defecto usar configuración de desarrollo
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()