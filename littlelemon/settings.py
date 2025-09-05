"""
Django settings for littlelemon project – Cloud Run/Google Cloud ready

Notes:
- Loads secrets from .env locally OR from Google Secret Manager in Cloud Run.
- Uses django-environ for parsing DATABASE_URL and other settings.
- Supports Cloud SQL via Cloud SQL Auth Proxy (recommended in Cloud Run) or direct TCP.
- Serves static and media files from a Google Cloud Storage bucket via django-storages.
- Preserves your REST framework, Djoser, and JWT configuration.
"""
from pathlib import Path
import io
import os
from urllib.parse import urlparse

import environ

# Optional (only used when running on GCP):
try:
    import google.auth
    from google.cloud import secretmanager
except Exception:  # pragma: no cover – local/dev without GCP libs
    google = None
    secretmanager = None

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------------
# Secrets & environment loading (local .env OR Secret Manager on Cloud Run)
# ----------------------------------------------------------------------------
# Default DEBUG=False for safety in prod
env = environ.Env(DEBUG=(bool, False))
local_env_file = BASE_DIR / ".env"

# Try to populate GOOGLE_CLOUD_PROJECT for Secret Manager usage
if google is not None:
    try:
        _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
    except Exception:
        pass

if local_env_file.exists():
    # Local development: load from .env
    env.read_env(str(local_env_file))
elif os.getenv("TRAMPOLINE_CI"):
    # CI fallback – minimal placeholders
    placeholder = (
        f"SECRET_KEY=dummy\n"
        f"DEBUG=True\n"
        f"DATABASE_URL=sqlite:///{BASE_DIR / 'db.sqlite3'}\n"
        f"GS_BUCKET_NAME=\n"
    )
    env.read_env(io.StringIO(placeholder))
elif os.getenv("GOOGLE_CLOUD_PROJECT") and secretmanager is not None:
    # Cloud Run: pull a .env payload from Secret Manager
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    settings_name = os.getenv("SETTINGS_NAME", "django_settings")
    secret_path = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    client = secretmanager.SecretManagerServiceClient()
    payload = client.access_secret_version(name=secret_path).payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))
else:
    # As a last resort, rely on explicit environment variables already set
    # (e.g., when running in container locally with -e vars)
    pass

# ----------------------------------------------------------------------------
# Core settings
# ----------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

# Cloud Run service URLs → CSRF/Hosts/SSL
CLOUDRUN_SERVICE_URLS = env("CLOUDRUN_SERVICE_URLS", default="")
if CLOUDRUN_SERVICE_URLS:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in CLOUDRUN_SERVICE_URLS.split(",") if u.strip()]
    ALLOWED_HOSTS = [urlparse(u).netloc for u in CSRF_TRUSTED_ORIGINS]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
else:
    # Local/dev fallback
    ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["127.0.0.1", "localhost"]) 
    CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=["http://127.0.0.1", "http://localhost"]) 

# ----------------------------------------------------------------------------
# Applications
# ----------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'restaurant',
    'authorization',

    # Third‑party
    'rest_framework',
    'rest_framework_simplejwt',
    'djoser',
    'storages',  # for Google Cloud Storage
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'littlelemon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['restaurant/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'littlelemon.wsgi.application'

# ----------------------------------------------------------------------------
# Django REST Framework / Auth
# ----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "5/minute",
        "user": "25/hour",
    },
}

DJOSER = {
    "USER_ID_FIELD": "username",
    "LOGIN_FIELD": "username",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SERIALIZERS": {},
}

from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ----------------------------------------------------------------------------
# Database (Cloud SQL via DATABASE_URL; falls back to SQLite in dev)
# ----------------------------------------------------------------------------
# Examples:
#  - Postgres via proxy: postgres://USER:PASSWORD@127.0.0.1:5432/DBNAME
#  - MySQL via proxy:    mysql://USER:PASSWORD@127.0.0.1:3306/DBNAME
#  - SQLite (dev):       sqlite:///path/to/db.sqlite3
DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Keep connections open (Cloud Run instances are reused)
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=600)

# If using the Cloud SQL Auth Proxy, set host/port explicitly
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY"):
    host = env("DB_HOST", default="127.0.0.1")
    port = env.int("DB_PORT", default=5432)  # use 3306 for MySQL
    DATABASES["default"].update({"HOST": host, "PORT": port})

# ----------------------------------------------------------------------------
# Internationalization
# ----------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------------
# Static & media files – Google Cloud Storage via django-storages
# ----------------------------------------------------------------------------
# Bucket must exist and the service account must have storage.admin (or granular perms).
GS_BUCKET_NAME = env("GS_BUCKET_NAME", default=None)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

if GS_BUCKET_NAME:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        },
    }
    # Optional: make uploaded media publicly readable by default (adjust to your needs)
    GS_DEFAULT_ACL = env("GS_DEFAULT_ACL", default="publicRead")
    # Optional: custom location prefixes inside the bucket
    GS_LOCATION = env("GS_LOCATION", default="")
else:
    # Local dev: use filesystem
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT = BASE_DIR / 'media'

# ----------------------------------------------------------------------------
# Security hardening for production
# ----------------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# ----------------------------------------------------------------------------
# Auth redirects (kept from your original settings)
# ----------------------------------------------------------------------------
MEDIA_URL = '/media/'
LOGIN_URL = '/login'

# ----------------------------------------------------------------------------
# Default primary key
# ----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
