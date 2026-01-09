from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# NUNCA deixar hardcoded em produção
SECRET_KEY = 'django-insecure-o10(c6z45(wq6ur=5ju$c!ln!-=^2yqs=tp3bhzp3b=)amtp^8'

# Em produção deve ser False
DEBUG = False

ALLOWED_HOSTS = [
    ".vercel.app",
    "localhost",
    "127.0.0.1",
]

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
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

# Deve existir app = get_wsgi_application() em SGTFC/wsgi.py
WSGI_APPLICATION = 'SGTFC.wsgi.app'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'PJsvXqimekzpfOGEiqpGxrOuKfBzvYHK',
        'HOST': 'tramway.proxy.rlwy.net',
        'PORT': '35690',
    }
}

AUTH_USER_MODEL = "Coordenacao.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = [os.path.join(BASE_DIR, 'staticfiles')]


# Evita erro se a pasta static não existir
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]

# Necessário para HTTPS na Vercel
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
