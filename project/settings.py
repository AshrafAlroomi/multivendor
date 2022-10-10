"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%eckd70i##mznm!a55p^yb&3unlw3!r)d3_g*=1zrx$_*_hy^5'
DEFAULT_DECIMAL_PLACES = 2
DEFAULT_MAX_DIGITS = 12
CURRENCIES = ('USD', 'SAR')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["nest.apexcode.info",
                 "www.nest.apexcode.info", "127.0.0.1", "127.0.0.1:8000","salis-multivendor-api.herokuapp.com"]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
# Application definition

INSTALLED_APPS = [
    # General use templates & template tags (should appear first)
    'adminlte3',
    # Optional: Django admin theme (must be before django.contrib.admin)
    'adminlte3_theme',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'captcha',
    'currencies',
    'home',
    'categories',
    'products',
    'accounts',
    'orders',
    'suppliers',
    'supplier_panel',
    'ckeditor',
    'crispy_forms',
    # 'FAQ',
    'newsletters',
    'blog',
    'reports',
    'settings',
    'contact',
    'pages',
    'payments',
    'rest_framework',
    'special_deals',
    'silk',
    'djmoney',
    'drf_yasg',
    'mptt',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'currencies.context_processors.currencies',
                'categories.context_processors.category_obj',
                'products.context_processors.new_products_obj',
                # 'orders.context_processors.orders_cart_obj',
                'home.context_processors.DealTime_obj',
                'home.context_processors.vendor_details_ad_image',
                'home.context_processors.shop_ad_sidebar',
                'home.context_processors.hot_deal_ad',
                'home.context_processors.head_text_ad',
                'settings.context_processors.socail_links_settings',
                'settings.context_processors.contact_info_settings',
                'settings.context_processors.support_number_settings',
                'settings.context_processors.site_settings',
                'pages.context_processors.pages_list_obj',

            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     },
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.AllowAny',
#     ],
# }
#


PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(PROJECT_DIR, 'salis.db'),
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'salis',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT':'',
#         'OPTIONS': {
#         'sql_mode': 'traditional',
#     }
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

###DEFAULT_CURRENCY##
DEFAULT_CURRENCY = 'USD'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'site_static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
                'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Form', 'Checkbox', 'Radio', 'TextField', 'Image',
                'Textarea', 'Select', 'Button', 'HiddenField']

        ]
    }
}

CRISPY_TEMPLATE_PACK = 'uni_form'

## STRIPE SETTINGS ##
STRIPE_PUBLIC_KEY = ""
STRIPE_SECRET_KEY = ""
STRIPE_WEBHOOK_SECRET = ""
# domain EX: example.com
YOUR_DOMAIN = "nest.apexcode.info"
# very important
# Set your Endpoint_URL in your stripe account WEBHOOK like this : https://YOUR_DOMAIN/orders/webhook/


# ClientInfo For Aramex
ARAMEX_USERNAME = ""
ARAMEX_PASSWORD = ""
ARAMEX_VERSION = "v1.0"
ARAMEX_ACCOUNTNUMBER = ""
ARAMEX_ACCOUNTPIN = ""

ARAMEX_ACCOUNTENTITY = ""
ARAMEX_ACCOUNTCOUNTRYCODE = ""
ARAMEX_SOURCE = "24"

ARAMEX_PRODUCTGROUP = "EXP"
ARAMEX_PRODUCTTYPE = "PPX"


# #Smtp Email for recovery password
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = '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'
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
EMAIL_SENDGRID = "selemhamed2016@gmail.com"

# silk config
LOGGING = {
    'version': 1,
    'formatters': {
        'mosayc': {
            'format': '%(asctime)-15s %(levelname)-7s %(message)s [%(funcName)s (%(filename)s:%(lineno)s)]',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'mosayc'
        }
    },
    'loggers': {
        'silk': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    },
}


# ie if Heroku server
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}