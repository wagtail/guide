from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = "testing-secret-key"

# Don't redirect to HTTPS in tests.
SECURE_SSL_REDIRECT = False
# Don't send the HSTS header
SECURE_HSTS_SECONDS = 0

# By default, Django uses a computationally difficult algorithm for passwords hashing.
# We don't need such a strong algorithm in tests, so use MD5
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Use non-manifest static files in tests, to avoid the need to run `collectstatic`
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
}
