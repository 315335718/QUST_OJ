"""
Django settings for QUST_OJ project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*293)87u=845v-yi$!-!f!igqr&l1ucpz*go1hv!)j%)vre&ws'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # my app
    'home',
    'account',
    'polygon',
    'problem',
    'schoolclass',
    'submission',
    'dispatcher',
    'contest',

    # third
    'django_jinja',
    'django_q',
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

ROOT_URLCONF = 'QUST_OJ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'environment': 'QUST_OJ.jinja2_env.environment',
            'extensions': [
                "jinja2.ext.do",
                "django_jinja.builtins.extensions.CsrfExtension",
            ],
        },
    },
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

WSGI_APPLICATION = 'QUST_OJ.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'QUST_OJ',
        'USER' : 'root',
        'PASSWORD' : 'xxx824650123',
        'HOST' : '127.0.0.1',
        'PORT' : '3306',
    }
}



# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'UTC'
TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

# USE_TZ = True
UES_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_URL = '/static/' # 只有起别名的作用
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    ("img", STATIC_ROOT / "img"),
    ("css", STATIC_ROOT / "css"),
    ("js", STATIC_ROOT / "js"),
]
# 当运行 python manage.py collectstatic 的时候
# STATIC_ROOT 文件夹 是用来将所有STATICFILES_DIRS中所有文件夹中的文件，以及各app中static中的文件都复制过来
# 把这些文件放到一起是为了部署的时候更方便

AUTH_USER_MODEL = 'account.User'

LOGOUT_REDIRECT_URL = '/'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PASSWORD": "mysecret"
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

Q_CLUSTER = {
    'name': 'QUST_OJ',#项目名称
    'workers': 10,  #worker数。默认为当前主机的CPU计数，
    'recycle': 500,  # worker在回收之前要处理的任务数。有助于定期释放内存资源。默认为500。
    'timeout': 600,  # 任务超时设置 10分钟
    'retry': 1200,
    'max_attempts': 1, # Limit the number of retry attempts for failed tasks. Set to 0 for infinite retries. Defaults to 0
    'cached': 3600,
    'save_limit': 250,  # 限制保存到Django的成功任务的数量。0为无限，-1则不会保存
    'queue_limit': 20,  # 排队的任务数量，默认为workers**2。
    'cpu_affinity': 1,  # 设置每个工作人员可以使用的处理器数量。
    'django_redis': 'default',
    'label': 'WARNING',  # 用于Django Admin页面的标签。
}