from .base import *  # noqa

DEBUG = False

SECRET_KEY = env["SECRET_KEY"]  # noqa

if allowed_hosts := env.get("ALLOWED_HOSTS"):  # noqa
    ALLOWED_HOSTS = allowed_hosts.split(",")

MANIFEST_LOADER["cache"] = True  # noqa
