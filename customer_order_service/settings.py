import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from firebase_setup import initialize_firebase

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key for the Django project; keep this secret in production!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-$qfi93p0%m_2%6!3xc)o(i%wlgp-ftup91t&47*te=-b!yr6zu')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# Allowed hosts for the application (set in production)
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Add other allowed hosts if necessary


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'customerorder',
    'rest_framework',  # Django REST Framework
    'oauth2_provider',  # OAuth2 provider
    'drf_spectacular',  # API schema generation
    'drf_spectacular_sidecar',  # Sidecar for serving Swagger UI
    'oidc_provider',  # OpenID Connect provider
]

# Africa's Talking API credentials
AFRICASTALKING_USERNAME = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
AFRICASTALKING_API_KEY = os.getenv('AFRICASTALKING_API_KEY', 'atsk_9c5a548336fa8a1fa3a9d6a8b43d1de098e82e41e98a958890f4b12fd5e98b1c669b47f7')

# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',  # Content Security Policy middleware
    'oidc_provider.middleware.SessionManagementMiddleware',  # Session management for OIDC
]

# API documentation settings
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
OIDC_USERINFO = 'customerorder.oidc_views.userinfo'  # Path to user info function
OIDC_IDTOKEN_EXPIRE = 3600  # ID token expiration time
OIDC_CODE_EXPIRE = 600  # Code expiration time
OIDC_EXTRA_SCOPE_CLAIMS = 'customerorder.oidc_views.CustomScopeClaims'  # Custom claims

# Content Security Policy settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "https://cdnjs.cloudflare.com")
CSP_SCRIPT_SRC = ("'self'", "https://cdnjs.cloudflare.com")

# Root URL configuration
ROOT_URLCONF = 'customer_order_service.urls'

# Firebase configuration
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')
FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n')  # Handle newlines in the private key
FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL')

# Initialize Firebase
initialize_firebase()
AUTH_USER_MODEL = 'customerorder.User'

# Firebase OIDC Configuration
OIDC_PROVIDER = {
    'OIDC_PROVIDER_BASE_URL': f'https://{FIREBASE_PROJECT_ID}.firebaseapp.com',
}

# OIDC client configuration
OIDC_RP_CLIENT_ID = FIREBASE_APP_ID
OIDC_RP_CLIENT_SECRET = None  # OIDC client secret (set if needed)
OIDC_OP_AUTHORIZATION_ENDPOINT = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}'
OIDC_OP_TOKEN_ENDPOINT = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}'
OIDC_OP_USER_ENDPOINT = f'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}'

# Database settings (using SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Path to the SQLite database file
    }
}

# Password validation settings
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

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'  # URL to access static files

# Default auto field setting
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directory for custom templates
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
