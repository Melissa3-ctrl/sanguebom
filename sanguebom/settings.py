from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# CONFIGURAÇÕES PRINCIPAIS
# =========================================================

SECRET_KEY = 'django-insecure-sua-chave-aqui'

DEBUG = True

ALLOWED_HOSTS = []


# =========================================================
# APLICATIVOS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'membros',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================================================
# URLS
# =========================================================

ROOT_URLCONF = 'sanguebom.urls'


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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


# =========================================================
# SERVIDOR
# =========================================================

WSGI_APPLICATION = 'sanguebom.wsgi.application'


# =========================================================
# BANCO DE DADOS
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================================================
# VALIDAÇÃO DE SENHA
# =========================================================

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


# =========================================================
# IDIOMA E HORÁRIO
# =========================================================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# =========================================================
# ARQUIVOS ESTÁTICOS
# =========================================================

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# =========================================================
# CONFIGURAÇÃO PADRÃO DO BANCO
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================================
# AUTENTICAÇÃO
# =========================================================

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'agendar_doacao'

LOGOUT_REDIRECT_URL = 'login'


# =========================================================
# CONFIGURAÇÃO DE E-MAIL
# =========================================================

# ⚠️ IMPORTANTE:
# Deixei o modo CONSOLE ativado para você testar a recuperação
# de senha sem precisar configurar e-mail real.
# O código de verificação vai aparecer no TERMINAL onde o
# runserver está rodando.

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ---------------------------------------------------------
# QUANDO FOR USAR E-MAIL REAL, DESCOMENTE ESSAS LINHAS
# E APAGUE A LINHA DO CONSOLE ACIMA
# ---------------------------------------------------------

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'SEU_EMAIL@gmail.com')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'SUA_SENHA_DE_APP')
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER