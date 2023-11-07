"""
Monkey patch the language code regular expressions `language_code_re` and `language_code_prefix_re`.

This allows the URL language prefix pattern to contain `.` (dots). Needed for Wagtail version numbers.

Valid examples:
- `/en-latest/`
- `/en-3.0/`
- `/en-4.0.x/`
"""
import logging
import re

from django.conf import settings
from django.utils import translation
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import get_language_info as original_get_language_info
from django.utils.translation import trans_real

logger = logging.getLogger(__name__)
logger.warning(
    "Monkey patching `language_code_re`, `language_code_prefix_re`, and `get_language_info`"
)

# PATCH: allow dots in language code
trans_real.language_code_re = _lazy_re_compile(
    r"^[a-z]{1,8}(?:-[a-z0-9.]{1,8})*(?:@[a-z0-9]{1,20})?$", re.IGNORECASE
)
trans_real.language_code_prefix_re = _lazy_re_compile(
    r"^/(\w+([@-](?:[\w\.])+){0,2})(/|$)"
)


def remove_version_number_from_language_code(lang_code):
    # Make sure to remove the version only if it exists
    if any(version in lang_code for version in settings.WAGTAIL_GUIDE_VERSIONS):
        return lang_code.rsplit("-", maxsplit=1)[0]
    return lang_code


def patched_get_language_info(lang_code):
    # PATCH: remove version number before continuing with the original function
    lang_code = remove_version_number_from_language_code(lang_code)
    return original_get_language_info(lang_code)


translation.get_language_info = patched_get_language_info
