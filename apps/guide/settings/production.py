from .base import *  # noqa

DEBUG = False

MANIFEST_LOADER["cache"] = True  # noqa

try:
    from .local import *  # noqa
except ImportError:
    pass
