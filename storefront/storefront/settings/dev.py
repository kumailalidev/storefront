from .common import *

DEBUG = True

SECRET_KEY = "django-insecure-t%kks32gm%3=6uvr09%$niy2xqbuk$)!h@e6fcct)x$8@7y-hm"


if DEBUG:
    INSTALLED_APPS += [
        "silk",
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "silk.middleware.SilkyMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MySQL_DB_NAME"),
        "HOST": os.environ.get("MySQL_HOST"),
        "PORT": os.environ.get("MySQL_PORT"),
        "USER": os.environ.get("MySQL_USER"),
        "PASSWORD": os.environ.get("MySQL_PASSWORD"),
    }
}
