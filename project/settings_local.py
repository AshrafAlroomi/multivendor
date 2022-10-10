from project.settings import *
from datetime import timedelta

# NOTE : Create db locally with same name
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]

INSTALLED_APPS.append('corsheaders')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'multi-vendor',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

LOGGING = None  # disable logging for local
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
}
