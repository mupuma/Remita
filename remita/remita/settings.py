
import os
from pathlib import Path

import webapp


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-0123456789!@#$%^&*(-_=+)abcdefghijkl-production0123456789!@#$%^&*(-_=+)mnopqrstuvwxyz')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'webapp',
    
]
AUTHENTICATION_BACKENDS = [
    'webapp.backends.authBackend.RoleBackend',
    'django.contrib.auth.backends.ModelBackend'
]
AUTH_USER_MODEL = 'webapp.Users'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = 'remita.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'remita.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Example using Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mupumamgtsdev@gmail.com'
EMAIL_HOST_PASSWORD = 'ptrcailrtlrrkwde'  # Use an app password if 2FA is enabled
DEFAULT_FROM_EMAIL = 'mupumamgtsdev@gmail.com'

REMITA_API_PUBLIC_KEY= 'C9MEL4NMZM7CNM5M'
REMITA_API_SECRET_KEY= 'N7VSULFSJW25CEMQ740DNM8236JDIA3N'

REMITA_API_AUTH_URL = 'https://demo.remita.net/remita/exapp/api/v1/send/api/uaasvc/uaa/token'
REMITA_API_BANK_LIST_URL='https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/banks'
REMITA_API_ACCOUNT_LOOKUP_URL='https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/account/lookup'
REMITA_API_BULK_PAYMENT_URL='https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment'
REMITA_API_BULK_PAYMENT_STATUS_URL='f"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment/status/{batch_ref}"'
REMITA_API_BULK_PAYMENT_DETAILS_URL='f"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment/details/{batch_ref}"'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'payment_integration',
        'USER': 'root',
        'PASSWORD': 'PassW0rd!23',
        'HOST': 'localhost',
        'PORT': '3306'
    },

    # SQL Server databases, each NAME changed to match the alias
    'ACCDAT': {
        'ENGINE': 'mssql',
        'NAME': 'ACCDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'ADADAT': {
        'ENGINE': 'mssql',
        'NAME': 'ADADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'ANRDAT': {
        'ENGINE': 'mssql',
        'NAME': 'ANRDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'APTDAT': {
        'ENGINE': 'mssql',
        'NAME': 'APTDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'ASPDAT': {
        'ENGINE': 'mssql',
        'NAME': 'ASPDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'BEADAT': {
        'ENGINE': 'mssql',
        'NAME': 'BEADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'BEGDAT': {
        'ENGINE': 'mssql',
        'NAME': 'BEGDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'BRIDAT': {
        'ENGINE': 'mssql',
        'NAME': 'BRIDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'BUFDAT': {
        'ENGINE': 'mssql',
        'NAME': 'BUFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'BUTDAT': {
        'ENGINE': 'mssql',
        'NAME': 'BUTDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'CAMDAT': {
        'ENGINE': 'mssql',
        'NAME': 'CAMDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'CASDAT': {
        'ENGINE': 'mssql',
        'NAME': 'CASDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'CIPDAT': {
        'ENGINE': 'mssql',
        'NAME': 'CIPDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'CLEDAT': {
        'ENGINE': 'mssql',
        'NAME': 'CLEDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'D2EDAT': {
        'ENGINE': 'mssql',
        'NAME': 'D2EDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'EFADAT': {
        'ENGINE': 'mssql',
        'NAME': 'EFADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'ENHDAT': {
        'ENGINE': 'mssql',
        'NAME': 'ENHDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'EQUDAT': {
        'ENGINE': 'mssql',
        'NAME': 'EQUDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'EXCDAT': {
        'ENGINE': 'mssql',
        'NAME': 'EXCDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'EXPDAT': {
        'ENGINE': 'mssql',
        'NAME': 'EXPDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'FELDAT': {
        'ENGINE': 'mssql',
        'NAME': 'FELDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'GC7DAT': {
        'ENGINE': 'mssql',
        'NAME': 'GC7DAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'GDRSDA': {
        'ENGINE': 'mssql',
        'NAME': 'GDRSDA',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'GESDAT': {
        'ENGINE': 'mssql',
        'NAME': 'GESDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'GFSDAT': {
        'ENGINE': 'mssql',
        'NAME': 'GFSDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'GFTBSR': {
        'ENGINE': 'mssql',
        'NAME': 'GFTBSR',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'GFTDAT': {
        'ENGINE': 'mssql',
        'NAME': 'GFTDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'H3ADAT': {
        'ENGINE': 'mssql',
        'NAME': 'H3ADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'HAFDAT': {
        'ENGINE': 'mssql',
        'NAME': 'HAFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'HEPDAT': {
        'ENGINE': 'mssql',
        'NAME': 'HEPDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'HOMDAT': {
        'ENGINE': 'mssql',
        'NAME': 'HOMDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'IEVDAT': {
        'ENGINE': 'mssql',
        'NAME': 'IEVDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'IGHDAT': {
        'ENGINE': 'mssql',
        'NAME': 'IGHDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'IHVGDA': {
        'ENGINE': 'mssql',
        'NAME': 'IHVGDA',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    },
    'IHVPAD': {
        'ENGINE': 'mssql',
        'NAME': 'IHVPAD',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'IHVSDA': {
        'ENGINE': 'mssql',
        'NAME': 'INVSDA',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'IMADAT': {
        'ENGINE': 'mssql',
        'NAME': 'IMADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'IMPDAT': {
        'ENGINE': 'mssql',
        'NAME': 'IMPDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'IMUDAT': {
        'ENGINE': 'mssql',
        'NAME': 'IMUDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'INFDAT': {
        'ENGINE': 'mssql',
        'NAME': 'INFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'IRCDAT': {
        'ENGINE': 'mssql',
        'NAME': 'IRCDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'ISEDAT': {
        'ENGINE': 'mssql',
        'NAME': 'ISEDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'ITADAT': {
        'ENGINE': 'mssql',
        'NAME': 'ITADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    
    'LSTDAT': {
        'ENGINE': 'mssql',
        'NAME': 'LSTDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'MALDAT': {
        'ENGINE': 'mssql',
        'NAME': 'MALDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'NDBSDA': {
        'ENGINE': 'mssql',
        'NAME': 'NDBSDA',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'NORDAT': {
        'ENGINE': 'mssql',
        'NAME': 'NORDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'OUTDAT': {
        'ENGINE': 'mssql',
        'NAME': 'OUTDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'PAVDAT': {
        'ENGINE': 'mssql',
        'NAME': 'PAVDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'PEDDAT': {
        'ENGINE': 'mssql',
        'NAME': 'PEDDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'PLADAT': {
        'ENGINE': 'mssql',
        'NAME': 'PLADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'RECDAT': {
        'ENGINE': 'mssql',
        'NAME': 'INFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'RSLDAT': {
        'ENGINE': 'mssql',
        'NAME': 'RSLDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SAFDAT': {
        'ENGINE': 'mssql',
        'NAME': 'SAFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SCEDAT': {
        'ENGINE': 'mssql',
        'NAME': 'SCEDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SGHDAT': {
        'ENGINE': 'mssql',
        'NAME': 'INFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SPEDAT': {
        'ENGINE': 'mssql',
        'NAME': 'SPEDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'STADAT': {
        'ENGINE': 'mssql',
        'NAME': 'STADAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SYNDAT': {
        'ENGINE': 'mssql',
        'NAME': 'SYNDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'TICDAT': {
        'ENGINE': 'mssql',
        'NAME': 'TICDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'TIFDAT': {
        'ENGINE': 'mssql',
        'NAME': 'TIFDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'TRIDAT': {
        'ENGINE': 'mssql',
        'NAME': 'TRIDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'VERDAT': {
        'ENGINE': 'mssql',
        'NAME': 'VERDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'WANDAT': {
        'ENGINE': 'mssql',
        'NAME': 'WANDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'WONDAT': {
        'ENGINE': 'mssql',
        'NAME': 'WONDAT',
        'USER': 'sa',
        'PASSWORD': 'sage300@ihvn',
        'HOST': '10.10.165.21',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/remita/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

