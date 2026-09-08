"""
Django settings for bmk_api_project.

Configuration is driven by environment variables so the same code runs
locally and in Docker. See `.env.example` at the repo root.
"""

from datetime import timedelta
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.environ.get(name)
    if raw is None:
        return list(default or [])
    return [item.strip() for item in raw.split(',') if item.strip()]


SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-qu&_#1)v5@$a7&b6dqaga5pi!v(o)zh!i2pns#d@3yu8)^=x1l',
)

DEBUG = env_bool('DJANGO_DEBUG', True)

# Shared with the UI (VITE_APP_DOMAIN). School sites are {slug}.{APP_DOMAIN}
APP_DOMAIN = (
    os.environ.get('APP_DOMAIN')
    or os.environ.get('VITE_APP_DOMAIN')
    or 'localhost'
).strip().lower()

# Always allow local/docker service names; extend via DJANGO_ALLOWED_HOSTS
# (comma-separated). Use "*" only for quick VM demos — lock down in production.
_base_hosts = ['localhost', '127.0.0.1', '.localhost', 'api', 'web']
_extra_hosts = env_list(
    'DJANGO_ALLOWED_HOSTS',
    ['localhost', '127.0.0.1', '.localhost', 'api', 'web'],
)
ALLOWED_HOSTS = list(dict.fromkeys([*_base_hosts, *_extra_hosts]))

_base_csrf = [
    'http://localhost',
    'http://127.0.0.1',
    'http://localhost:80',
    'http://127.0.0.1:80',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://uk.telugu.localhost',
    'http://balavikas.localhost',
    'http://uk.telugu.localhost:80',
    'http://balavikas.localhost:80',
    'http://uk.telugu.localhost:8080',
    'http://balavikas.localhost:8080',
]
CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys([*_base_csrf, *env_list('DJANGO_CSRF_TRUSTED_ORIGINS', [])])
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'authentication',
    'core',
    'school',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# WhiteNoise is required in Docker; optional for local runserver if not installed yet.
import importlib.util

_WHITENOISE = importlib.util.find_spec('whitenoise') is not None
if _WHITENOISE:
    MIDDLEWARE.insert(2, 'whitenoise.middleware.WhiteNoiseMiddleware')


ROOT_URLCONF = 'bmk_api_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bmk_api_project.wsgi.application'

# Database: Postgres when DATABASE_URL / POSTGRES_* are set, otherwise SQLite.
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL.startswith('postgres'):
    # postgres://user:pass@host:5432/db
    # Prefer explicit POSTGRES_* when provided (simpler in Compose).
    import urllib.parse as urlparse

    parsed = urlparse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/') or 'bmk',
            'USER': parsed.username or 'bmk',
            'PASSWORD': parsed.password or '',
            'HOST': parsed.hostname or 'localhost',
            'PORT': str(parsed.port or 5432),
        }
    }
elif os.environ.get('POSTGRES_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'bmk'),
            'USER': os.environ.get('POSTGRES_USER', 'bmk'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'bmk'),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Reasonable avatar upload limit (UI + API enforce this).
MAX_AVATAR_BYTES = int(os.environ.get('MAX_AVATAR_BYTES', str(100 * 1024)))  # 100 KB

# Homework / teacher session materials: local (Docker volume) or azure_blob
HOMEWORK_STORAGE_BACKEND = os.environ.get('HOMEWORK_STORAGE_BACKEND', 'local').strip().lower()
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', '').strip()
AZURE_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', '').strip()
AZURE_STORAGE_ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY', '').strip()
AZURE_STORAGE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER', 'bmk-homework').strip() or 'bmk-homework'
AZURE_BLOB_SAS_EXPIRY_HOURS = int(os.environ.get('AZURE_BLOB_SAS_EXPIRY_HOURS', '24'))

_storages: dict = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}
if _WHITENOISE:
    _storages['staticfiles'] = {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    }
else:
    _storages['staticfiles'] = {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    }

_azure_ready = bool(
    AZURE_STORAGE_CONNECTION_STRING
    or (AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY)
)
if HOMEWORK_STORAGE_BACKEND == 'azure_blob' and _azure_ready:
    _azure_options: dict = {
        'azure_container': AZURE_STORAGE_CONTAINER,
        'expiration_secs': max(AZURE_BLOB_SAS_EXPIRY_HOURS, 1) * 3600,
        'overwrite_files': False,
        'timeout': 60,
    }
    if AZURE_STORAGE_CONNECTION_STRING:
        _azure_options['connection_string'] = AZURE_STORAGE_CONNECTION_STRING
    else:
        _azure_options['account_name'] = AZURE_STORAGE_ACCOUNT_NAME
        _azure_options['account_key'] = AZURE_STORAGE_ACCOUNT_KEY
    _storages['azure_homework'] = {
        'BACKEND': 'storages.backends.azure_storage.AzureStorage',
        'OPTIONS': _azure_options,
    }
elif HOMEWORK_STORAGE_BACKEND == 'azure_blob' and not _azure_ready:
    # Misconfigured Azure — keep local so the app still boots; uploads stay on volume.
    HOMEWORK_STORAGE_BACKEND = 'local'

STORAGES = _storages


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Shared secret for Sikshavahini → BMK class catalog calls
SIKSHAVAHINI_SHARED_SECRET = os.environ.get('SIKSHAVAHINI_SHARED_SECRET', '').strip()
SUNAADAM_SHARED_SECRET = os.environ.get('SUNAADAM_SHARED_SECRET', '').strip()

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

AUTH_USER_MODEL = 'authentication.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5174',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
    ],
)

CORS_ALLOWED_ORIGIN_REGEXES = env_list(
    'CORS_ALLOWED_ORIGIN_REGEXES',
    [
        r'^http://([a-z0-9-]+\.)?localhost:5173$',
        r'^http://([a-z0-9-]+\.)?localhost:5174$',
        r'^http://([a-z0-9-]+\.)?localhost:8080$',
    ],
)

CORS_ALLOW_ALL_ORIGINS = env_bool('CORS_ALLOW_ALL_ORIGINS', DEBUG)

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-school-slug',
]

# Useful behind Nginx / reverse proxies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# --- Email (confirmation + password reset) ---
# Default: print emails to API logs (Docker-friendly for Test/Staging).
# For real SMTP set EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD in .env
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Balamukundam Vidyalayam <noreply@balamukundam.com>',
)
# Apex site used to build {slug}.{domain} links in emails
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', '').rstrip('/')
FRONTEND_PORT = os.environ.get('FRONTEND_PORT', '')
