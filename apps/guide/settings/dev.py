from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-@at*b!q74k70i)^#bu@yz@u9_79754+als*%(q_o60s+i+(2b6"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += [  # noqa
    "django_extensions",
]

# Disable forcing HTTPS locally since development server supports HTTP only.
SECURE_SSL_REDIRECT = False
# For the same reason the HSTS header should not be sent.
SECURE_HSTS_SECONDS = 0


try:
    from .local import *  # noqa
except ImportError:
    pass
