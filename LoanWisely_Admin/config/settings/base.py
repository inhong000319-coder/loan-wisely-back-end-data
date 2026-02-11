from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

_allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h for h in _allowed_hosts.split(",") if h] if not DEBUG else []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",

    "apps.common",
    "apps.auth",
    "apps.policies",
    "apps.metadata",
    "apps.approvals",
    "apps.audits",
    "apps.recommendations",
    "apps.rawfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "apps.common.middleware.JwtAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

MANAGEMENT_BASE_PATH = "/management"

SPRING_BASE_URL = os.environ.get("SPRING_BASE_URL", "http://localhost:8080")
SPRING_TIMEOUT_SECS = int(os.environ.get("SPRING_TIMEOUT_SECS", "10"))
SPRING_ADMIN_TOKEN_HEADER = os.environ.get("SPRING_ADMIN_TOKEN_HEADER", "Authorization")
SPRING_ADMIN_LOGIN_PATH = os.environ.get("SPRING_ADMIN_LOGIN_PATH", "/api/admin/auth/login")
SPRING_ADMIN_VERIFY_PATH = os.environ.get("SPRING_ADMIN_VERIFY_PATH", "/api/admin/auth/verify")
SPRING_ADMIN_TOKEN = os.environ.get("SPRING_ADMIN_TOKEN", "")

JWT_COOKIE_NAME = os.environ.get("JWT_COOKIE_NAME", "admin_jwt")
JWT_HEADER_NAME = os.environ.get("JWT_HEADER_NAME", "Authorization")
JWT_VERIFY_WITH_SPRING = os.environ.get("JWT_VERIFY_WITH_SPRING", "true").lower() == "true"
JWT_JWKS_URL = os.environ.get("JWT_JWKS_URL", "")

CSRF_COOKIE_NAME = os.environ.get("CSRF_COOKIE_NAME", "csrf_token")
_csrf_trusted = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [h for h in _csrf_trusted.split(",") if h] if not DEBUG else []

USE_MOCK_DATA = os.environ.get("USE_MOCK_DATA", "false").lower() == "true"
DISABLE_AUTH = os.environ.get("DISABLE_AUTH", "false").lower() == "true"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
