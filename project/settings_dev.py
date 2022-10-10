from project.settings import *
from datetime import timedelta
import pymysql

pymysql.install_as_MySQLdb()
# NOTE : Create db locally with same name
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "158.101.226.132"]
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://158.101.226.132',
    'http://0.0.0.0',
    'http://127.0.0.1',
    'http://158.101.226.132:80',
    'http://158.101.226.132:3000',
    'http://158.101.226.132:8000'
]

INSTALLED_APPS.append('corsheaders')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'salis_multivendor_api',
        'USER': 'salis',
        'PASSWORD': '12345678!@#Aa',
        'HOST': '65.108.72.55',
        'PORT': 3306,
    }
}

LOGGING = None  # disable logging for local
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
}
