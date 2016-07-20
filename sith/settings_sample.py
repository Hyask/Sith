"""
Django settings for sith project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(4sjxvhz@m5$0a$j0_pqicnc$s!vbve)z+&++m%g%bjhlz4+g2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_jinja',
    'core',
    'club',
    'subscription',
    'accounting',
    'counter',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'sith.urls'

TEMPLATES = [
    {
        "NAME": "jinja2",
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "app_dirname": "templates",
            "newstyle_gettext": True,
            "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.template.context_processors.tz",
                    "django.contrib.messages.context_processors.messages",
                ],
            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.with_",
                "jinja2.ext.i18n",
                "jinja2.ext.autoescape",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
            ],
            "filters": {
                "markdown": "core.templatetags.renderer.markdown",
            },
            "globals": {
                "can_edit_prop": "core.views.can_edit_prop",
                "can_edit": "core.views.can_edit",
                "can_view": "core.views.can_view",
                "get_subscriber": "subscription.views.get_subscriber",
                "settings": "sith.settings",
            },
            "bytecode_cache": {
                "name": "default",
                "backend": "django_jinja.cache.BytecodeCache",
                "enabled": False,
            },
            "autoescape": True,
            "auto_reload": DEBUG,
            "translation_engine": "django.utils.translation",
        }
    },
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

WSGI_APPLICATION = 'sith.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

# Medias
MEDIA_ROOT = './data/'
MEDIA_URL = '/data/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Auth configuration

AUTH_USER_MODEL = 'core.User'
AUTH_ANONYMOUS_MODEL = 'core.models.AnonymousUser'
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/'
DEFAULT_FROM_EMAIL="bibou@git.an"

# Email
EMAIL_HOST="localhost"
EMAIL_PORT=25

# AE configuration
SITH_MAIN_CLUB = {
        'name': "AE",
        'unix_name': "ae",
        'address': "6 Boulevard Anatole France, 90000 Belfort"
        }

# Bar managers
SITH_BAR_MANAGER = {
        'name': "BdF",
        'unix_name': "bdf",
        'address': "6 Boulevard Anatole France, 90000 Belfort"
        }

# Define the date in the year serving as reference for the subscriptions calendar
# (month, day)
SITH_START_DATE = (8, 15) # 15th August

SITH_GROUPS = {
    'root': {
        'id': 1,
        'name': "Root",
    },
    'public': {
        'id': 2,
        'name': "Not registered users",
    },
    'accounting-admin': {
        'id': 3,
        'name': "Accounting admin",
    },
    'counter-admin': {
        'id': 4,
        'name': "Counter admin",
    },
}

SITH_BOARD_SUFFIX="-board"
SITH_MEMBER_SUFFIX="-members"

SITH_MAIN_BOARD_GROUP=SITH_MAIN_CLUB['unix_name']+SITH_BOARD_SUFFIX
SITH_MAIN_MEMBERS_GROUP=SITH_MAIN_CLUB['unix_name']+SITH_MEMBER_SUFFIX

SITH_ACCOUNTING_PAYMENT_METHOD = [
        ('cheque', _('Check')),
        ('cash', _('Cash')),
        ('transfert', _('Transfert')),
        ('card', _('Credit card')),
        ]

SITH_SUBSCRIPTION_PAYMENT_METHOD = [
        ('cheque', _('Check')),
        ('cash', _('Cash')),
        ('other', _('Other')),
        ]

SITH_COUNTER_BARS = [
        (1, "Foyer"),
        (2, "MDE"),
        (3, "La Gommette"),
        ]

SITH_COUNTER_PAYMENT_METHOD = [
        ('cheque', _('Check')),
        ('cash', _('Cash')),
        ]

SITH_COUNTER_BANK = [
        ('other', 'Autre'),
        ('la-poste', 'La Poste'),
        ('credit-agricole', 'Credit Agricole'),
        ('credit-mutuel', 'Credit Mutuel'),
        ]

# Subscription durations are in semestres (should be settingized)
SITH_SUBSCRIPTIONS = {
    'un-semestre': {
        'name': _('One semester'),
        'price': 15,
        'duration': 1,
    },
    'deux-semestres': {
        'name': _('Two semesters'),
        'price': 28,
        'duration': 2,
    },
    'cursus-tronc-commun': {
        'name': _('Common core cursus'),
        'price': 45,
        'duration': 4,
    },
    'cursus-branche': {
        'name': _('Branch cursus'),
        'price': 45,
        'duration': 6,
    },
# To be completed....
}

SITH_CLUB_ROLES = {
        10: _('President'),
        9: _('Vice-President'),
        7: _('Treasurer'),
        5: _('Communication supervisor'),
        4: _('Secretary'),
        3: _('IT supervisor'),
        2: _('Board member'),
        1: _('Active member'),
        0: _('Curious'),
        }

# This corresponds to the maximum role a user can freely subscribe to
# In this case, SITH_MAXIMUM_FREE_ROLE=1 means that a user can set himself as "Membre actif" or "Curieux", but not higher
SITH_MAXIMUM_FREE_ROLE=1

# Minutes to timeout the logged barmen
SITH_BARMAN_TIMEOUT=20
