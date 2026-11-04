"""Invalidate the llms.txt server-side cache when page content changes.

The llms.txt views cache their rendered output (see apps.llms_txt.views).
That output depends on the live page tree: which pages exist, their URLs, and
their content. Those only change through publishing, unpublishing, slug
changes, moves, or deletions.
"""

from django.db.models.signals import post_delete
from wagtail.models import Page
from wagtail.signals import (
    page_published,
    page_slug_changed,
    page_unpublished,
    post_page_move,
)

from apps.llms_txt.views import invalidate_cache


def invalidate_llms_txt_cache(sender, **kwargs):
    invalidate_cache()


def register_signals():
    page_published.connect(invalidate_llms_txt_cache)
    page_unpublished.connect(invalidate_llms_txt_cache)
    page_slug_changed.connect(invalidate_llms_txt_cache)
    post_page_move.connect(invalidate_llms_txt_cache)
    post_delete.connect(invalidate_llms_txt_cache, sender=Page)
