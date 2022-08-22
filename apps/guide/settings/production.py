from .base import *  # noqa

DEBUG = False

SECRET_KEY = env["SECRET_KEY"]  # noqa

ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")  # noqa

MANIFEST_LOADER["cache"] = True  # noqa
