"""
Django settings module for configuring the application.

This module contains the configuration for environment variables, middleware, installed apps, database settings,
logging, API documentation, Firebase integration, and other essential Django settings.

Modules Imported:
-----------------
1. os: Standard library for interacting with the operating system and file paths.
2. Path (from pathlib): Object-oriented filesystem paths, suitable for handling file and directory paths.
3. environ: Library for managing environment variables in Django applications.
4. initialize_firebase (from config.firebase.firebase_setup): Custom function to set up Firebase integration.
"""

# Standard library import for interacting with the operating system and environment variables
import os

# Provides a powerful object-oriented way to handle filesystem paths
from pathlib import Path

# Django-environ library for handling environment variables and type casting
import environ

# Custom module to initialize Firebase with environment variables and project-specific settings
from config.firebase.firebase_setup import initialize_firebase

# Initialize environment variables with default types and values
env = environ.Env(
    DEBUG=(bool, False),  # Set default DEBUG mode to False
    ALLOWED_HOSTS=(str, 'localhost,127.0.0.1'),  # Default allowed hosts
    CORS_ALLOWED_ORIGINS=(str, 'http://localhost:4200,http://127.0.0.1:4200'),  # Default CORS origins
)

# Define BASE_DIR: The base directory of the Django project
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to app/main

# Define the path to the .env file relative to BASE_DIR
ENV_PATH = BASE_DIR.parent / '.env'  # Points to customer-order-system/.env

# Load environment variables from the .env file
environ.Env.read_env(str(ENV_PATH))

# Django core settings
SECRET_KEY = env('SECRET_KEY')  # Secret key for cryptographic signing
DEBUG = env('DEBUG')  # Debug mode for development
ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')  # List of allowed hosts

# Installed apps: Django and third-party applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.customerorder',  # Custom app for customer order functionality
    'rest_framework',  # Django REST framework for API development
    'oauth2_provider',  # OAuth2 provider for authentication
    'drf_spectacular',  # API schema generation
    'drf_spectacular_sidecar',  # Sidecar files for Spectacular
    'oidc_provider',  # OpenID Connect provider
]

# Africa's Talking API credentials for SMS and communication integration
AFRICASTALKING_USERNAME = env('AFRICASTALKING_USERNAME')
AFRICASTALKING_API_KEY = env('AFRICASTALKING_API_KEY')

# Middleware: Layers for processing requests and responses
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security-related headers
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session management
    'django.middleware.common.CommonMiddleware',  # Basic middleware for request handling
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Authentication middleware
    'django.contrib.messages.middleware.MessageMiddleware',  # Message framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
    'csp.middleware.CSPMiddleware',  # Content Security Policy middleware
    'oidc_provider.middleware.SessionManagementMiddleware',  # OIDC session management
]

# Spectacular settings: Configuration for generating API documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'CUSTOMER_ORDER APIS',
    'DESCRIPTION': 'CO SYSTEM',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,  # Include schema in API response
    'SWAGGER_UI_DIST': 'SIDECAR',  # Use Spectacular's sidecar files for Swagger UI
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',  # Use Spectacular's sidecar files for ReDoc
}

# OIDC settings: OpenID Connect configuration for authentication
OIDC_SESSION_MANAGEMENT_ENABLE = True
OIDC_USERINFO = 'app.customerorder.authentication.oidc_views.userinfo'
OIDC_IDTOKEN_EXPIRE = 3600  # ID token expiration time in seconds
OIDC_CODE_EXPIRE = 600  # Authorization code expiration time in seconds
OIDC_EXTRA_SCOPE_CLAIMS = 'app.customerorder.authentication.oidc_views.CustomScopeClaims'

# Content Security Policy (CSP): Security settings for resource loading
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "https://cdnjs.cloudflare.com")
CSP_SCRIPT_SRC = ("'self'", "https://cdnjs.cloudflare.com")

# Root URL configuration
ROOT_URLCONF = 'app.main.urls'

# Firebase configuration: Environment-based settings for Firebase integration
FIREBASE_API_KEY = env('FIREBASE_API_KEY')
FIREBASE_PROJECT_ID = env('FIREBASE_PROJECT_ID')
FIREBASE_AUTH_DOMAIN = env('FIREBASE_AUTH_DOMAIN')
FIREBASE_DATABASE_URL = env('FIREBASE_DATABASE_URL')
FIREBASE_STORAGE_BUCKET = env('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = env('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = env('FIREBASE_APP_ID')
FIREBASE_PRIVATE_KEY = env('FIREBASE_PRIVATE_KEY').replace('\\n', '\n')  # Replace escaped newlines
FIREBASE_CLIENT_EMAIL = env('FIREBASE_CLIENT_EMAIL')

# Initialize Firebase (runs only once during startup)
initialize_firebase()

# Custom user model: Replaces the default Django user model
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

# Database configuration: Uses PostgreSQL with credentials from environment variables
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

# Password validation: Strengthening user authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization: Language and time zone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = 'static/'  # URL for serving static files
STATIC_ROOT = "/cust_backend/staticfiles"  # Path for collecting static files

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Templates configuration
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

# CORS Allowed Origins: Specify trusted domains for cross-origin requests
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS').split(',')

# Logging configuration: File and console-based logging
LOGGING_LEVEL = env('LOGGING_LEVEL', default='ERROR')  # Default logging level
LOGGING_FILE_PATH = env('LOGGING_FILE_PATH', default='error.log')  # File path for logs
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
