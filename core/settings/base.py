"""
Configuración base que es común entre todos los entornos.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent 
# Ajustamos para la nueva estructura

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kudl3o#czu*ez4_p6h86_6dod@8fr$zc3h@y9t6t&cwgoeu#wt') 
# Valor por defecto solo para desarrollo

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Aplicaciones propias
    'tienda',
    'usuarios',
    'catalogo',
    'carrito',
    'pedidos',
    'pagos',
    'core',
    # Bibliotecas de terceros
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'imagekit',
    'django_cleanup',
    'compressor',
    
]

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',  # En desarrollo usamos la memoria local
        'LOCATION': 'mototienda-cache',
        'TIMEOUT': 300,  # 5 minutos en segundos
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Número máximo de entradas en la caché
        }
    }
}

# La configuración correcta del middleware de caché
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # Debe estar primero
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.LoginRateLimitMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.SecurityAuditMiddleware',
    'utils.exception_middleware.GlobalExceptionMiddleware',
    'utils.monitoring.PerformanceMonitorMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # Debe estar último
]

# Configuración de archivos estáticos
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',  # Añadir CompressorFinder
]

# Configuración de compressor
COMPRESS_ENABLED = True
# Pre-comprimir en producción
COMPRESS_OFFLINE = True

COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': '/static/',
    'MEDIA_URL': '/media/',
}  
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_PRECOMPILERS = ()
COMPRESS_URL = '/static/'
COMPRESS_ROOT = '/media/'
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_HASHING_METHOD = 'content'
# Permitir URLs externas
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

COMPRESS_OUTPUT_DIR = 'compressed'

# Middleware de cacheo

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carrito.context_processors.carrito_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # PCI DSS requiere mínimo 12 caracteres
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Tiempo de vida de la sesión - 15 minutos de inactividad (900 segundos)
SESSION_COOKIE_AGE = 900
# Actualizar el tiempo de sesión en cada petición
SESSION_SAVE_EVERY_REQUEST = True  

# Política de cookies más segura
# Solo enviar cookies en conexiones HTTPS
SESSION_COOKIE_SECURE = True  
# Solo enviar cookies CSRF en conexiones HTTPS
CSRF_COOKIE_SECURE = True 
# Prevenir acceso JavaScript a la cookie de sesión    
SESSION_COOKIE_HTTPONLY = True  
# Prevenir acceso JavaScript a la cookie CSRF
CSRF_COOKIE_HTTPONLY = True     

# Configuraciones de seguridad HTTP

 # Activa filtro XSS en navegadores
SECURE_BROWSER_XSS_FILTER = True 
 # Previene MIME-sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True 
# Previene clickjacking - no permite ser incrustado en frames
X_FRAME_OPTIONS = 'DENY'  

# Internationalization
LANGUAGE_CODE = 'es-es'
# Ajusta a tu zona horaria
TIME_ZONE = 'America/Guatemala'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Configuración para mensajes con Bootstrap
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# URL de login
LOGIN_URL = 'usuarios:login'



# Configuración de logging base - se aplicará a todos los entornos
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/mototienda.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'formatter': 'verbose',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/performance.log'),
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/audit.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'mototienda': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'mototienda.error': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'mototienda.security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'mototienda.performance': {
            'handlers': ['performance_file', 'console'],
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

LOGIN_REDIRECT_URL = 'tienda:inicio'

# Asegurar que existe el directorio para logs
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.makedirs(os.path.join(BASE_DIR, 'logs'))