from pathlib import Path
import os
from datetime import timedelta

# ======================================================
# RUTAS Y CONFIGURACIÓN BÁSICA
# ======================================================

# BASE_DIR: directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================
# CLAVES Y DEBUG
# ======================================================

# Clave secreta de Django
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-^j2&dyz6s@hy%b99mn9h@x59ebw%517mflsr^jne%n+ysql@&d"
)
# DEBUG: si es True, Django muestra errores detallados
# Por defecto activamos DEBUG en local para evitar problemas
# de archivos estáticos (Swagger UI) cuando no se ha hecho collectstatic.
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Hosts permitidos para este proyecto (producción)
ALLOWED_HOSTS = [
    "pagina-web-finansas-b6474cfcee14.herokuapp.com",  # Backend antiguo en Heroku
    "pagina-web-finansas.herokuapp.com",               # App Heroku actual
    "web-front-hffd.onrender.com",                     # Frontend en Render
    "127.0.0.1",                                      # Local
    "localhost",                                      # Local
    "testserver",                                      # Cliente de pruebas de Django
]

# ======================================================
# APLICACIONES INSTALADAS
# ======================================================

INSTALLED_APPS = [
    # Apps predeterminadas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Terceros
    'drf_yasg',                      # Generación de documentación Swagger
    'rest_framework',                 # Django REST Framework
    'rest_framework_simplejwt.token_blacklist', # JWT blacklisting
    'django_filters',                 # Filtros para DRF
    'corsheaders',                    # Manejo de CORS
    
    # Apps locales
    'users', 
    'ingresos', 
    'egresos', 
    'ahorros', 
    'prestamos',
]

# ======================================================
# MIDDLEWARE
# ======================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Seguridad general
    'whitenoise.middleware.WhiteNoiseMiddleware',             # Para servir archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',    # Manejo de sesiones
    'corsheaders.middleware.CorsMiddleware',                  # CORS: debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',              # Funciones comunes (redirects, etc)
    'django.middleware.csrf.CsrfViewMiddleware',              # Protección CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',# Autenticación de usuarios
    'django.contrib.messages.middleware.MessageMiddleware',   # Mensajes flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Protección clickjacking
]

# ======================================================
# URLS Y TEMPLATES
# ======================================================

ROOT_URLCONF = 'web.urls'  # Archivo principal de URLs

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # Motor de templates
        'DIRS': [],   # Directorios adicionales de templates
        'APP_DIRS': True,  # Buscar templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',   # Permite usar request en templates
                'django.contrib.auth.context_processors.auth',  # Datos de usuario en templates
                'django.contrib.messages.context_processors.messages', # Mensajes flash
            ],
        },
    },
]

WSGI_APPLICATION = 'web.wsgi.application'  # Aplicación WSGI para despliegue

# ======================================================
# BASE DE DATOS
# ======================================================

import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,  # pooling en Heroku
    )
}

# ======================================================
# VALIDACIÓN DE CONTRASEÑAS
# ======================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, # Evita contraseñas similares al username
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},           # Longitud mínima
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},          # Evita contraseñas comunes
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},         # Evita contraseñas solo numéricas
]

# ======================================================
# INTERNACIONALIZACIÓN
# ======================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ======================================================
# DJANGO REST FRAMEWORK + JWT
# ======================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Autenticación con JWT
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Requiere login por defecto
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Vida del token de acceso
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     # Vida del refresh token
    "ROTATE_REFRESH_TOKENS": True,                   # Rotar refresh tokens al usar
    "BLACKLIST_AFTER_ROTATION": True,               # Añadir tokens rotados a blacklist
}

# ======================================================
# CORS
# ======================================================

# Dominios permitidos para hacer fetch desde frontend
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",                # Local
    "http://localhost:5500",                # Local
    "http://127.0.0.1:5501",                # Live Server alternativo
    "http://localhost:5501",                # Live Server alternativo
    "https://web-front-hffd.onrender.com",  # Render front
]

# ======================================================
# ARCHIVOS ESTÁTICOS
# ======================================================

STATIC_URL = 'static/'                 # URL para servir archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles' # Carpeta donde collectstatic pone los archivos

STATICFILES_DIRS = [
    BASE_DIR / "static",               # Carpeta adicional para buscar archivos estáticos
]

# ======================================================
# USER MODEL PERSONALIZADO
# ======================================================

AUTH_USER_MODEL = 'users.User'  # Modelo de usuario personalizado

# ======================================================
# EMAIL
# ======================================================

# Para desarrollo local (puedes activar si quieres depuración)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# Para producción (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')       # Usuario SMTP desde variable de entorno
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')   # Contraseña SMTP desde variable de entorno
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ======================================================
# CAMPO POR DEFECTO PARA PK
# ======================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# En Heroku (DEBUG=False), usa /tmp para archivos de media (FS efímero pero escribible)
if not DEBUG:
    MEDIA_ROOT = Path('/tmp') / 'media'

# ======================================================
# SWAGGER / OpenAPI
# ======================================================

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer <token>"',
        }
    },
}

# ======================================================
# STATICFILES STORAGE (WhiteNoise)
# ======================================================
if not DEBUG:
    # En producción usamos el storage con manifiesto
    # (requiere ejecutar collectstatic antes de desplegar)
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Seguridad detrás de proxy (Heroku)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Confianza CSRF en dominios conocidos
CSRF_TRUSTED_ORIGINS = [
    'https://pagina-web-finansas.herokuapp.com',
    'https://pagina-web-finansas-b6474cfcee14.herokuapp.com',
    'https://web-front-hffd.onrender.com',
]

# Asegura que la URL de estáticos sea absoluta para que funcione en rutas como /docs/
STATIC_URL = "/static/"
