from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = "testing-secret-key"

# Exercise frontend cache signals without requiring Cloudflare credentials.
if "wagtail.contrib.frontend_cache" not in INSTALLED_APPS:  # noqa: F405
    INSTALLED_APPS = [*INSTALLED_APPS, "wagtail.contrib.frontend_cache"]  # noqa: F405
WAGTAILFRONTENDCACHE = {
    "default": {"BACKEND": "wagtail.contrib.frontend_cache.backends.dummy.DummyBackend"}
}

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

# Task queue configuration to ensure tasks run immediately in the test environment
# https://docs.wagtail.org/en/stable/releases/6.4.html#background-tasks-run-at-end-of-current-transaction
TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "ENQUEUE_ON_COMMIT": False,
    }
}
