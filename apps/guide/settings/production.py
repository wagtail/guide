from .base import *  # noqa

DEBUG = False
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
try:
    from .local import *  # noqa
except ImportError:
    pass
