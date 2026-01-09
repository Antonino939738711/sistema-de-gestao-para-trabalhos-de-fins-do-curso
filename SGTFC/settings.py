import os
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURANÇA
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-uod+*=%7@x**swxug7=sfcom6nlrcbu@8z^1gjy4ch30jnoyp8')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Configuração de Hosts para Vercel e Local
ALLOWED_HOSTS = ["*", ".vercel.app", "6bc4a50434b2.ngrok-free.app", "localhost", "127.0.0.1"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Coordenacao',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SGTFC.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'SGTFC.wsgi.application'

# Banco de Dados - Railway PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'PJsvXqimekzpfOGEiqpGxrOuKfBzvYHK',
        'HOST': 'postgres.railway.internal',
        'PORT': '5432',
    }
}

# Usuário Personalizado
AUTH_USER_MODEL = "Coordenacao.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configurações de CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://6bc4a50434b2.ngrok-free.app",
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos (Configuração para Vercel)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'