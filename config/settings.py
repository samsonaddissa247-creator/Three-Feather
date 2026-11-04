import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured  # pyright: ignore[reportMissingModuleSource]

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-me')
DEBUG = os.environ.get('DEBUG', '1') == '1'
if not DEBUG and SECRET_KEY == 'dev-only-change-me':
    raise ImproperlyConfigured('Set the SECRET_KEY environment variable when DEBUG is off.')
def _parse_csv_env(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]

ALLOWED_HOSTS = _parse_csv_env(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,feathersclub.vercel.app,.vercel.app',
)
CSRF_TRUSTED_ORIGINS = _parse_csv_env(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000,https://localhost,https://127.0.0.1,https://feathersclub.vercel.app,https://*.vercel.app',
)

COACH_PASSWORD = os.environ.get('COACH_PASSWORD', 'COACHAB')

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'club',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

DB_PATH = os.environ.get('DB_PATH', '/tmp/db.sqlite3' if os.environ.get('VERCEL') else BASE_DIR / 'db.sqlite3')
if isinstance(DB_PATH, str):
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
else:
    db_dir = str(DB_PATH.parent)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': DB_PATH}}

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Africa/Harare'
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 60 * 60 * 8
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
