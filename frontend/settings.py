import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY desde ENV (fallback para desarrollo local)
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-v02#l*vz09z2er+2f^nri*$0jw^(uk+*26_5-0m-eeqt8n(ed*")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "asiricarritos.onrender.com,localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "usuarios",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
ROOT_URLCONF = 'frontend.urls'

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

WSGI_APPLICATION = 'frontend.wsgi.application'
# Database (usa DATABASE_URL si está presente)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "asiridata_usuarios"),
        "USER": os.environ.get("DB_USER", "asiridata"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "123456789Asiri"),
        "HOST": os.environ.get("DB_HOST", "mysql-asiridata.alwaysdata.net"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "CONN_MAX_AGE": 0,
    }
}
DATABASES["default"] = dj_database_url.config(default=os.environ.get("DATABASE_URL",
    f"mysql://{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}@{DATABASES['default']['HOST']}/{DATABASES['default']['NAME']}"),
    conn_max_age=600)
# Configuración de la base de datos para Render (usa DATABASE_URL si está presente)
DATABASES['default'] = dj_database_url.config(default=f"mysql://{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}@{DATABASES['default']['HOST']}/{DATABASES['default']['NAME']}", conn_max_age=600)


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'usuarios.Usuario'  # Usar modelo de usuario personalizado


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True  # Permitir peticiones externas (solo para pruebas)
# Email (SendGrid)
# EMAIL_BACKEND = "sendgrid_django.SendgridBackend"
# SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
# SENDGRID_SANDBOX_MODE_IN_DEBUG = False
# SENDGRID_ECHO_TO_STDOUT = True
# DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "asiri.carrito@example.com")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "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").strip()
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "asiri.carrito@example.com")

# Configurar EMAIL_BACKEND de forma condicional:
# - Si hay SENDGRID_API_KEY usar sendgrid_django backend
# - Si no, usar backend de consola (evita errores en desarrollo y permite ver el email)
if SENDGRID_API_KEY:
    EMAIL_BACKEND = "sendgrid_django.SendgridBackend"
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
    SENDGRID_ECHO_TO_STDOUT = False
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
    SENDGRID_ECHO_TO_STDOUT = False


