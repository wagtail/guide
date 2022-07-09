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

from django.utils.translation import trans_real
from django.utils.regex_helper import _lazy_re_compile


logger = logging.getLogger(__name__)
logger.warning("Monkey patching `language_code_re` and `language_code_prefix_re`")

trans_real.language_code_re = _lazy_re_compile(
    r"^[a-z]{1,8}(?:-[a-z0-9.]{1,8})*(?:@[a-z0-9]{1,20})?$", re.IGNORECASE
)
trans_real.language_code_prefix_re = _lazy_re_compile(r"^/([\w+]{2}-[\w.]*)(/|$)")
