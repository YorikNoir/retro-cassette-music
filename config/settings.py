"""
Django settings for Retro Cassette Music Generator project.
"""

from pathlib import Path
import environ
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'apps.accounts',
    'apps.songs',
    'apps.library',
    'apps.generation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = env('STATIC_ROOT', default=BASE_DIR / 'staticfiles')

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=BASE_DIR / 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# AI Model Settings
MODELS_PATH = env('MODELS_PATH', default='../checkpoints')
VAE_PATH = env('VAE_PATH', default='../checkpoints/vae')
ACESTEP_MODEL = env('ACESTEP_MODEL', default='acestep-v15-turbo')
LLM_MODEL = env('LLM_MODEL', default='acestep-5Hz-lm-0.6B')
EMBEDDING_MODEL = env('EMBEDDING_MODEL', default='Qwen3-Embedding-0.6B')

# GPU Configuration
USE_GPU = env.bool('USE_GPU', default=True)
CUDA_VISIBLE_DEVICES = env('CUDA_VISIBLE_DEVICES', default='0')

# LLM API Settings
LLM_PROVIDER = env('LLM_PROVIDER', default='local')  # openai, comet, or local
OPENAI_API_KEY = env('OPENAI_API_KEY', default=None)
COMET_API_KEY = env('COMET_API_KEY', default=None)
# OpenAI client appends /chat/completions, so base URL should end in /v1
COMET_API_BASE_URL = env('COMET_API_BASE_URL', default='https://api.cometapi.com/v1')

# Encryption for API keys
ENCRYPTION_KEY = env('ENCRYPTION_KEY', default=None)

# Field encryption (for django-encrypted-model-fields)
# Generate a secure key for production using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Development default key (CHANGE IN PRODUCTION!)
FIELD_ENCRYPTION_KEY = env('ENCRYPTION_KEY', default='8xyRCz-6DvW4H7nL9qN2Y3mP5tB6uJ4kE1sA7dF8gH0=')

# Background Task Configuration
# Using simple threading for async tasks (no external services needed)
MAX_CONCURRENT_TASKS = env.int('MAX_CONCURRENT_TASKS', default=3)

# File Upload Settings
MAX_UPLOAD_SIZE = env.int('MAX_UPLOAD_SIZE', default=10485760)  # 10MB

# Rate Limiting
GENERATION_RATE_LIMIT = env.int('GENERATION_RATE_LIMIT', default=10)
