"""
Django settings for do_it_django_prj project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os    # MEDIA 파일 디렉토리 지정을 위해 import
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-f&ns#60fhnshh_!cw9l-emsb_r!h4f4!o-@au%e@#3h6+ezi-z')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', 1)) # 환경 파일의 DEBUG 정보를 우선 시 하고, 없으면 '1'을 사용

# 환경 변수
if os.environ.get('DJANGO_ALLOWED_HOSTS'):
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')
else:
    ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.sites',

    # django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'crispy_forms',
    'markdownx',
    'blog',
    'single_pages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'do_it_django_prj.urls'

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

WSGI_APPLICATION = 'do_it_django_prj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('SQL_DATABASE', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432')
    }
}




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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '_static')
# 해당 웹사이트의 주소/port 다음에 오는 /media/가 오면 미디어 파일의 url임
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '_media')

# media 파일이 저장될 디렉토리를 BASE_DIR을 이용하여 지정
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# django-crispy-forms 사용
CRISPY_TEMPLATE_PACK = 'bootstrap'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend'
]

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True  # 가입 시 이메일 주소 수집
ACCOUNT_EMAIl_VERIFICATION = 'none'   # 가입 시 이메일 전송을 통한 확인 과정 진행

LOGIN_REDIRECT_URL ='/blog/'  # 로그인 후 보여지는 페이지를 /blog/ 로 지정
