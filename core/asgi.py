"""
ASGI config for core project.
"""
import os
from pathlib import Path
import dotenv
from django.core.asgi import get_asgi_application

# Cargar variables de entorno
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
if dotenv_path.exists():
    dotenv.load_dotenv(str(dotenv_path))

# Configurar para producción por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')

application = get_asgi_application()