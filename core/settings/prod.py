"""
Configuración para el entorno de producción.
"""
from .base import * 
# Importamos la configuración base
import os

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn="TU_DSN_DE_SENTRY",  # Reemplaza esto con tu DSN real
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.5,  # Ajusta según tus necesidades
        send_default_pii=False,  # No enviar información personal identificable
        environment="production",
    )
    print("Sentry inicializado correctamente")
except ImportError:
    print("Sentry SDK no está instalado. La monitorización de errores estará desactivada.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Obtener hosts permitidos de la variable de entorno
# Si no hay ninguno, solo permitimos localhost por seguridad
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

# Secret key debe ser configurada en variables de entorno en producción
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise Exception("La clave secreta debe estar configurada en variables de entorno para producción.")

# Database - Postgres para producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mototienda'),
        'USER': os.environ.get('DB_USER', 'mototienda_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Configuración para archivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración avanzada para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Habilitar compresión GZIP para archivos estáticos
WHITENOISE_MIDDLEWARE = {
    'compression_enabled': True,
    'allow_all_origins': False,
    'add_headers_function': None,
}

# Optimizar compressión
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_HASHING_METHOD = 'content'  # Usar hash basado en contenido
COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage'

# Configuración para archivos de medios
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Seguridad para producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración HTTPS
SECURE_SSL_REDIRECT = True  # Redirige todo el tráfico a HTTPS
SESSION_COOKIE_SECURE = True  # Solo envía cookies a través de HTTPS
CSRF_COOKIE_SECURE = True     # Solo envía cookies a través de HTTPS
SESSION_COOKIE_HTTPONLY = True  # Previene que JavaScript acceda a cookies
CSRF_COOKIE_HTTPONLY = True     # Previene que JavaScript acceda a cookies

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email backend para producción (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Tiempo de sesión (1 hora de inactividad)
SESSION_COOKIE_AGE = 3600  # En segundos
SESSION_SAVE_EVERY_REQUEST = True

# Asegurar que existe el directorio para logs
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.makedirs(os.path.join(BASE_DIR, 'logs'))

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/mototienda.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/performance.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/audit.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'mototienda': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'mototienda.error': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'mototienda.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'mototienda.performance': {
            'handlers': ['performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'mototienda.audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuración de caché para producción - Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # Ignora errores para no interrumpir si Redis falla
            'PARSER_CLASS': 'redis.connection.HiredisParser',  # Parser más rápido
            'SOCKET_CONNECT_TIMEOUT': 5,  # Timeout de conexión
            'SOCKET_TIMEOUT': 5,  # Timeout de socket
        },
        'KEY_PREFIX': 'mototienda',
        'TIMEOUT': 3600,  # 1 hora
    }
}

# Usar Redis también para las sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'