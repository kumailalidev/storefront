import os
from celery import Celery

# Setting Django settings as environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storefront.settings")

# creating celery instance
celery = Celery("storefront")

# telling celery where it can find settings related to celery
celery.config_from_object(
    "django.conf:settings", namespace="CELERY"
)  # :settings is an object inside django.conf module. namespace tells all the settings will start with CELERY

# automatically discover all the tasks
celery.autodiscover_tasks()
