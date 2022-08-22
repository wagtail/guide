from .base import *  # noqa

DEBUG = False

SECRET_KEY = env["SECRET_KEY"]  # noqa

MANIFEST_LOADER["cache"] = True  # noqa

try:
    from .local import *  # noqa
except ImportError:
    pass
