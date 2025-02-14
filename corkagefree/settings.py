
from pathlib import Path
import os
import requests
import dotenv
from decouple import config






# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
dotenv.load_dotenv()

API_KEY=os.environ.get("SECRET_KEY")

SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '40.82.157.231', 'vscamsniffer.work.gd']



# Application definition

INSTALLED_APPS = [
    #비동치러리를 위한 ASGI 웹서버
    'daphne',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'users',
    'rp',

    #allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',

    #provider
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',

    #chat service
    'channels',
]


REST_USE_JWT = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':(
        'rest_framework_simplejwt.authentication.JWTAuthentication',
)}
#asgi 앱설정
ASGI_APPLICATION = 'corkagefree.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware", #소셜로그인
]

ROOT_URLCONF = 'corkagefree.urls'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
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
            ],
        },
    },
]

WSGI_APPLICATION = 'corkagefree.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ✅ CORS 설정 추가 (React와 Django 연결 가능)
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  # React 프론트엔드 주소
#     "http://40.82.157.231",# VM의 퍼블릭 IP
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://40.82.157.231:3000',  # React에서 API를 호출할 수 있도록 허용
    'https://vscamsniffer.work.gd',
]

CORS_ALLOW_CREDENTIALS = True  # 인증정보 허용
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://40.82.157.231",
    "http://40.82.157.231:3000",
    "https://vscamsniffer.work.gd",  # HTTPS 기반 도메인 추가
]



# 소셜로그인 구현시 작성
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


SITE_ID = 2
REST_USE_JWT = True
LOGIN_REDIRECT_URL ='/'
LOGOUT_REDIRECT_URL = "http://localhost:3000/"


LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = "https://vscamsniffer.work.gd/"



ACCOUNT_LOGIN_ON_GET = True  # GET 요청 시 바로 로그인 수행
SOCIALACCOUNT_LOGIN_ON_GET = True  # 소셜 계정도 GET 요청 시 바로 로그인
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'

#받아올정보
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
    'kakao': {
        'SCOPE': ['profile_nickname'],
    },
    'naver': {
        'SCOPE': ['profile_nickname'],
    }
}


# 프로젝트 루트 디렉토리 (BASE_DIR)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 미디어 파일 저장 경로 설정
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

