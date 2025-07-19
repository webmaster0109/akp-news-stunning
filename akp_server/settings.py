from pathlib import Path
import os
from urllib.parse import urlparse

try:
  from decouple import config
except ImportError:
  import os
  config = os.environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6txf^pg1^h9sxzf5wpj1g*kp0z67c)@)_ie#^($c(58rh_j%ty"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    "https://aajkaprahari.com",
]

# Application definition

INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django_ckeditor_5',
    "akp_news",
    "akp_accounts",
    "akp_epapers",
    "admin_akp",
]

AUTH_USER_MODEL = 'akp_accounts.CustomUser'

MAX_ADMIN_CONCURRENT_SESSIONS = 2
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "akp_server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "Base.utils.get_categories",
                "Base.utils.social_accounts_context",
            ],
        },
    },
]

WSGI_APPLICATION = "akp_server.wsgi.application"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake', # A unique name for this cache instance
    }
}

# Database
tmpPostgres = urlparse('postgresql://akp_news_owner:npg_ZzmU53FbAEgO@ep-ancient-firefly-a8mtjyub-pooler.eastus2.azure.neon.tech/akp_news?sslmode=require')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,

        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-in"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'public/static/')
# STATICFILES_DIR = {
#     os.path.join(BASE_DIR, 'public/static/')
# }
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'public/')

CLOUDFLARE_R2_BUCKET=config("CLOUDFLARE_R2_BUCKET")
CLOUDFLARE_R2_BUCKET_ENDPOINT=config("CLOUDFLARE_R2_BUCKET_ENDPOINT")
CLOUDFLARE_R2_ACCESS_KEY=config("CLOUDFLARE_R2_ACCESS_KEY")
CLOUDFLARE_R2_SECRET_KEY=config("CLOUDFLARE_R2_SECRET_KEY")

CLOUDFLARE_R2_CONFIG_OPTIONS = {
    "bucket_name": CLOUDFLARE_R2_BUCKET,
    "access_key": CLOUDFLARE_R2_ACCESS_KEY,
    "secret_key": CLOUDFLARE_R2_SECRET_KEY,
    "endpoint_url": CLOUDFLARE_R2_BUCKET_ENDPOINT,
    "default_acl": "public-read",
    "signature_version": "s3v4",
}

STORAGES = {
    "default": {
      "BACKEND": "akp_server.helpers.cloudflare.storages.MediaFileStorage",
      "OPTIONS": CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
    "staticfiles": {
      "BACKEND": "akp_server.helpers.cloudflare.storages.StaticFileStorage",
      "OPTIONS": CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
}

CKEDITOR_5_FILE_STORAGE = "akp_server.storage.CustomStorage"

customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(100, 100%, 30%)',
            'label': 'Green'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
        'toolbar_Custom': [
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
        ]

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    },
    "htmlSupport": {
        "allow": [
            {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
        ]
    },
}

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
