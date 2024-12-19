from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
print("path of BASE_DIR", BASE_DIR)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB (adjust as needed)""

SECRET_KEY = 'django-insecure-r@od8^&0xgfbv7(jz&8^l*@83*l3_a1=)$62=bd8%djeh)-(fp'

DEBUG = False 

X_FRAME_OPTIONS = 'DENY'

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
# SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 31536000  
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

ALLOWED_HOSTS = ["10.10.2.179", "cmogujarat.gov.in", "127.0.0.1"]

INSTALLED_APPS = [  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'drf_yasg',
    "corsheaders",
    "rest_framework",
    'djoser',
    'django_prometheus',
    'csp',
]

LOCAL_APPS = [
    'base',
    'app',
    'sentiment',
    'scrutiny',
    'wtc',
    'auth_app',
    'analytics'
]

INSTALLED_APPS += THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',   
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'base.middleware.CacheControlMiddleware',
    # 'base.middleware.SanitizeHeadersMiddleware',
    'base.middleware.SecurityHeadersMiddleware',  
    'base.middleware.XXSSProtectionMiddleware', 
    'base.middleware.HideSensitiveHeadersMiddleware',
    'base.middleware.RemoveHostnameMiddleware',
    'base.middleware.HideHostHeaderMiddleware',
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_file')    
]


STATIC_ROOT = os.path.join(BASE_DIR, 'static')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = [
#     "http://cmogujarat.gov.in",
#     "https://cmogujarat.gov.in",
#     "https://52.70.182.167",
#     "https://10.10.2.179",
#     "http://10.10.2.179",
#     "http://127.0.0.1"
# ]

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',  # Limit anonymous users to 5 requests per minute
        'user': '10/minute',  # Limit authenticated users to 10 requests per minute
    },
}

AUTH_USER_MODEL = 'auth_app.User'

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=20),  # Access token expires in 5 minutes
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),   # Refresh token expires in 30 days
    'ROTATE_REFRESH_TOKENS': False,                  # Whether to rotate the refresh token on use (optional)
    'BLACKLIST_AFTER_ROTATION': False,               # Whether to blacklist old refresh tokens (optional)
    'ALGORITHM': 'HS256',                            # Default JWT algorithm (optional)
    'SIGNING_KEY': SECRET_KEY,                       # Your JWT signing key (optional, defaults to the Django SECRET_KEY)
    'VERIFYING_KEY': None,                           # Key to verify the JWT (optional)
    'AUDIENCE': None,                                # Optional audience setting
    'ISSUER': None,                                  # Optional issuer setting
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme.'
        }
    }
}

LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django_prometheus.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "https://trustedscriptsource.com"]
CSP_STYLE_SRC = ["'self'", "https://trustedstylesource.com"]
CSP_IMG_SRC = ["'self'", "data:", "https://trustedimagesource.com"]

SECURE_PERMISSION_POLICY = "geolocation=(), microphone=(), camera=()"

# WHITENOISE_ALLOW_ALL_ORIGINS = True 
# WHITENOISE_MEDIA_PREFIX = MEDIA_URL 