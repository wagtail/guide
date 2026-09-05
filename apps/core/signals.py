"""Invalidate template fragment caches when page content changes.

Two fragments are cached via {% wagtailcache %} (see base.html):

- The header is cached per language. Its content depends on the live page
  tree: which pages are in the menu, their URLs, and their titles. Those only
  change through publishing, unpublishing, slug changes, moves, or deletions,
  and any of those can affect any language, so all languages are invalidated
  whenever any of those happens.

- The language selector is cached per language and page. The fragment for a
  page lists the page's live translations and their URLs, so it only goes
  stale when a page in the same translation group is published, unpublished,
  renamed, moved, or deleted. Renames and moves also change the URLs of the
  page's descendants, so their translation groups are invalidated too.
"""

from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_delete, pre_delete
from wagtail.models import Page
from wagtail.signals import (
    page_published,
    page_slug_changed,
    page_unpublished,
    post_page_move,
)

HEADER_CACHE_FRAGMENT = "header"
LANGUAGE_SELECTOR_CACHE_FRAGMENT = "language_selector"


def invalidate_header_cache():
    for language_code, _name in settings.WAGTAIL_CONTENT_LANGUAGES:
        key = make_template_fragment_key(HEADER_CACHE_FRAGMENT, [language_code])
        cache.delete(key)


def invalidate_language_selector_cache(page_ids):
    """Delete selector fragments for the given pages, in every language."""
    cache.delete_many(
        make_template_fragment_key(
            LANGUAGE_SELECTOR_CACHE_FRAGMENT, [language_code, page_id]
        )
        for page_id in page_ids
        for language_code, _name in settings.WAGTAIL_CONTENT_LANGUAGES
    )


def invalidate_language_selector_for_page(page):
    """Delete selector fragments for `page` and its translations.

    Publishing, unpublishing, or deleting `page` changes which translations
    are listed in the fragments of every page in its translation group.
    """
    page_ids = {page.id}
    if page.translation_key:
        page_ids.update(
            Page.objects.filter(translation_key=page.translation_key).values_list(
                "id", flat=True
            )
        )
    invalidate_language_selector_cache(page_ids)


def invalidate_language_selector_for_subtree(page):
    """Delete selector fragments for `page`'s subtree and their translations.

    Renaming or moving `page` changes the URLs of its whole subtree, which
    are listed in the fragments of those pages' translations.
    """
    translation_keys = Page.objects.descendant_of(page, inclusive=True).values_list(
        "translation_key", flat=True
    )
    page_ids = Page.objects.filter(translation_key__in=translation_keys).values_list(
        "id", flat=True
    )
    invalidate_language_selector_cache(page_ids)


def invalidate_caches_for_page_change(sender, instance, **kwargs):
    invalidate_header_cache()
    invalidate_language_selector_for_page(instance)


def invalidate_caches_for_url_change(sender, instance, **kwargs):
    invalidate_header_cache()
    invalidate_language_selector_for_subtree(instance)


def invalidate_header_cache_for_signal(sender, **kwargs):
    invalidate_header_cache()


def register_signals():
    page_published.connect(invalidate_caches_for_page_change)
    page_unpublished.connect(invalidate_caches_for_page_change)
    # pre_delete rather than post_delete so translation groups can still be
    # looked up before the pages are gone.
    pre_delete.connect(invalidate_caches_for_page_change, sender=Page)
    page_slug_changed.connect(invalidate_caches_for_url_change)
    post_page_move.connect(invalidate_caches_for_url_change)
    post_delete.connect(invalidate_header_cache_for_signal, sender=Page)
