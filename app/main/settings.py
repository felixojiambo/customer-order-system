import os
from pathlib import Path
import environ
from config.firebase.firebase_setup import initialize_firebase

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(str, 'localhost,127.0.0.1'),
    CORS_ALLOWED_ORIGINS=(str, 'http://localhost:4200,http://127.0.0.1:4200'),
)

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to app/main

# Define path to .env using BASE_DIR
ENV_PATH = BASE_DIR.parent / '.env'  # Points to customer-order-system/.env
environ.Env.read_env(str(ENV_PATH))

# Django core settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.customerorder',
    'rest_framework',
    'oauth2_provider',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'oidc_provider',
]

# Africa's Talking API credentials
AFRICASTALKING_USERNAME = env('AFRICASTALKING_USERNAME')
AFRICASTALKING_API_KEY = env('AFRICASTALKING_API_KEY')

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'oidc_provider.middleware.SessionManagementMiddleware',
]

# Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'CUSTOMER_ORDER APIS',
    'DESCRIPTION': 'CO SYSTEM',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# OIDC settings
OIDC_SESSION_MANAGEMENT_ENABLE = True
OIDC_USERINFO = 'app.customerorder.authentication.oidc_views.userinfo'
OIDC_IDTOKEN_EXPIRE = 3600
OIDC_CODE_EXPIRE = 600
OIDC_EXTRA_SCOPE_CLAIMS = 'app.customerorder.authentication.oidc_views.CustomScopeClaims'

# Content Security Policy settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "https://cdnjs.cloudflare.com")
CSP_SCRIPT_SRC = ("'self'", "https://cdnjs.cloudflare.com")

# Root URL configuration
ROOT_URLCONF = 'app.main.urls'
# Firebase configuration from environment
FIREBASE_API_KEY = env('FIREBASE_API_KEY')
FIREBASE_PROJECT_ID = env('FIREBASE_PROJECT_ID')
FIREBASE_AUTH_DOMAIN = env('FIREBASE_AUTH_DOMAIN')
FIREBASE_DATABASE_URL = env('FIREBASE_DATABASE_URL')
FIREBASE_STORAGE_BUCKET = env('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = env('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = env('FIREBASE_APP_ID')
FIREBASE_PRIVATE_KEY = env('FIREBASE_PRIVATE_KEY').replace('\\n', '\n')
FIREBASE_CLIENT_EMAIL = env('FIREBASE_CLIENT_EMAIL')

# Initialize Firebase (runs only once)
initialize_firebase()

# Custom user model
AUTH_USER_MODEL = 'customerorder.User'

# OIDC Provider and Client configuration for Firebase
OIDC_PROVIDER = {
    'OIDC_PROVIDER_BASE_URL': f'https://{FIREBASE_PROJECT_ID}.firebaseapp.com',
}
OIDC_RP_CLIENT_ID = FIREBASE_APP_ID
OIDC_RP_CLIENT_SECRET = None
OIDC_OP_AUTHORIZATION_ENDPOINT = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}'
OIDC_OP_TOKEN_ENDPOINT = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}'
OIDC_OP_USER_ENDPOINT = f'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}'

# Database configuration (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

STATIC_ROOT = "/cust_backend/staticfiles"


# Default auto field setting
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Templates configuration
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

# CORS Allowed Origins
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS').split(',')

# Logging Configuration
LOGGING_LEVEL = env('LOGGING_LEVEL', default='ERROR')
LOGGING_FILE_PATH = env('LOGGING_FILE_PATH', default='error.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOGGING_FILE_PATH,
            'formatter': 'verbose',
        },
        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': LOGGING_LEVEL,
    },
}
