"""Invalidate the header template fragment cache when page content changes.

The header is cached per language via {% wagtailcache %} (see base.html). Its
content depends on the live page tree: which pages are in the menu, their
URLs, and their titles. Those only change through publishing, unpublishing,
slug changes, moves, or deletions.
"""

from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_delete
from wagtail.models import Page
from wagtail.signals import (
    page_published,
    page_slug_changed,
    page_unpublished,
    post_page_move,
)

HEADER_CACHE_FRAGMENT = "header"


def invalidate_header_cache():
    for language_code, _name in settings.WAGTAIL_CONTENT_LANGUAGES:
        key = make_template_fragment_key(HEADER_CACHE_FRAGMENT, [language_code])
        cache.delete(key)


def invalidate_header_cache_for_signal(sender, **kwargs):
    invalidate_header_cache()


def register_signals():
    page_published.connect(invalidate_header_cache_for_signal)
    page_unpublished.connect(invalidate_header_cache_for_signal)
    page_slug_changed.connect(invalidate_header_cache_for_signal)
    post_page_move.connect(invalidate_header_cache_for_signal)
    post_delete.connect(invalidate_header_cache_for_signal, sender=Page)
