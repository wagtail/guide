from .test import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

DATABASES = {
    "default": dj_database_url.parse(  # noqa: F405
        f"sqlite:///{BASE_DIR / 'db_e2e.sqlite3'}"  # noqa: F405
    )
}

WAGTAILADMIN_BASE_URL = "http://127.0.0.1:8000"
