import os
from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
import dj_database_url
import cloudinary

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = True
ALLOWED_HOSTS = ["*"]

# 🔐 Tenant Configuration
TENANT_MODEL = "lms_project.Institution"
TENANT_DOMAIN_MODEL = "lms_project.Domain"
PUBLIC_SCHEMA_NAME = "public"
TENANT_URLCONF = "lms_project.tenant_urls"
PUBLIC_SCHEMA_URLCONF = "lms.urls"

# 🔧 App Configuration
SHARED_APPS = [
    'django_tenants',
    'core',  # must come before auth
    'lms_project',
    'auditlog',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

TENANT_APPS = [
    'core',
    'django.contrib.auth',
    'django.contrib.admin',
    # other tenant-scoped apps
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS] + [
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',
    'rest_framework',
]

# 🔐 Authentication
AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = [
    'core.backends.StrictEmailBackend',
    'core.backends.RegistrationNumberBackend',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# 🌍 Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

#  Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django_tenants.middleware.TenantMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🌐 URLs & Templates
ROOT_URLCONF = 'lms.urls'
WSGI_APPLICATION = 'lms.wsgi.application'

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

# 🗄️ Database
DATABASE_URL = os.getenv("DATABASE_URL")

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
}

# 🔥 FORCE django-tenants backend
DATABASES['default']['ENGINE'] = 'django_tenants.postgresql_backend'

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# 🔐 Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# ⚠️ Usitumie STATICFILES_DIRS kwenye Render isipokuwa una extra static folder
# STATICFILES_DIRS = [BASE_DIR / 'static']

# MEDIA FILES (Cloudinary)
MEDIA_URL = '/media/'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# CLOUDINARY CONFIG
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
)

print(os.getenv('CLOUDINARY_CLOUD_NAME'))



CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://umemeswahili.co.tz",
    "https://lms-0djt.onrender.com",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]





# 🧠 Default Primary Key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SECRET_KEY = os.getenv("SECRET_KEY")
ZENOPAY_API_KEY = os.getenv("ZENOPAY_API_KEY")