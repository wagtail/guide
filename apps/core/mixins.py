"""
Mixins for core app page models.
"""

from django.conf import settings
from django.utils import translation
from wagtail.coreutils import get_content_languages


class LocaleURLMixin:
    """
    Fix get_url_parts for combined language+version locale codes (e.g. en-latest).

    When the active language is a base code like "en" (e.g. from admin preferences),
    Wagtail substitutes it for the page's locale, producing /en/ instead of
    /en-latest/ and causing 404s for "View live" links. This mixin forces the page's
    locale when the active language is not a valid content language, so super() uses
    the correct URL prefix.
    """

    def get_url_parts(self, request=None):
        use_wagtail_i18n = getattr(settings, "WAGTAIL_I18N_ENABLED", False)
        if use_wagtail_i18n and translation.get_language() not in get_content_languages():
            with translation.override(self.locale.language_code):
                return super().get_url_parts(request=request)
        return super().get_url_parts(request=request)
