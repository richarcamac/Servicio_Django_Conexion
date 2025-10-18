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
    "sendgrid_django",
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

# Email (SendGrid)
EMAIL_BACKEND = "sendgrid_django.SendgridBackend"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "asiri.carrito@example.com")

