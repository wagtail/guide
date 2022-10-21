"""
Monkey patch the language code regular expressions `language_code_re` and `language_code_prefix_re`.

This allows the URL language prefix pattern to contain `.` (dots). Needed for Wagtail version numbers.

Valid examples:
- `/en-latest/`
- `/en-3.0/`
- `/en-4.0.x/`
"""
import re
import logging

from django.utils import translation
from django.utils.translation import get_language_info as original_get_language_info
from django.utils.translation import gettext_lazy, trans_real
from django.utils.regex_helper import _lazy_re_compile


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


def patched_get_language_info(lang_code):
    from django.conf.locale import LANG_INFO

    # PATCH: remove version number before continuing with the original function
    lang_code = lang_code.rsplit("-", maxsplit=1)[0]

    # Need to copy the original code instead of calling the original function
    # directly because there's a recursive call to `get_language_info` in the
    # original function.

    try:
        lang_info = LANG_INFO[lang_code]
        if "fallback" in lang_info and "name" not in lang_info:
            # PATCH: recurse with original function
            info = original_get_language_info(lang_info["fallback"][0])
        else:
            info = lang_info
    except KeyError:
        if "-" not in lang_code:
            raise KeyError("Unknown language code %s." % lang_code)
        generic_lang_code = lang_code.split("-")[0]
        try:
            info = LANG_INFO[generic_lang_code]
        except KeyError:
            raise KeyError(
                "Unknown language code %s and %s." % (lang_code, generic_lang_code)
            )

    if info:
        info["name_translated"] = gettext_lazy(info["name"])
    return info


translation.get_language_info = patched_get_language_info
