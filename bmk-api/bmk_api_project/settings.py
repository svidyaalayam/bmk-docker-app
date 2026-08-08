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
    'http://balamukundam.localhost',
    'http://balavikas.localhost',
    'http://balamukundam.localhost:80',
    'http://balavikas.localhost:80',
    'http://balamukundam.localhost:8080',
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
try:
    import whitenoise  # noqa: F401

    MIDDLEWARE.insert(2, 'whitenoise.middleware.WhiteNoiseMiddleware')
    _WHITENOISE = True
except ImportError:
    _WHITENOISE = False


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
if _WHITENOISE:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
