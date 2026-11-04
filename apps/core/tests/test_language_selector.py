from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import connection
from django.template import Context, Template
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import translation as translation_utils

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory


def language_selector_cache_key(page, language_code="en"):
    return make_template_fragment_key("language_selector", [language_code, page.pk])


class TestLanguageSelector(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.page = ContentPageFactory(parent=self.home)

    def add_translation(self, language_code):
        locale = LocaleFactory(language_code=language_code)
        home_translation = self.home.copy_for_translation(locale)
        home_translation.save_revision().publish()
        page_translation = self.page.copy_for_translation(locale)
        page_translation.save_revision().publish()
        return page_translation

    def render_selector(self, context=None):
        template = Template("{% load core_tags %}{% language_selector %}")
        # A normal request would go through LocaleMiddleware to activate the locale.
        with translation_utils.override("en"):
            return template.render(Context(context or {}))

    def test_inclusion_tag_lists_translations(self):
        self.add_translation("nl")
        self.add_translation("pt-br")

        result = self.render_selector({"page": self.page})

        self.assertIn('hreflang="nl"', result)
        self.assertIn('hreflang="pt-br"', result)
        self.assertIn('href="/nl/', result)
        self.assertIn('href="/pt-br/', result)

    def test_inclusion_tag_selects_locale(self):
        self.add_translation("nl")
        self.add_translation("pt-br")
        self.render_selector({"page": self.page})

        with CaptureQueriesContext(connection) as ctx:
            self.render_selector({"page": self.page})

        standalone_locale_queries = [
            query
            for query in ctx.captured_queries
            if query["sql"].startswith('SELECT "wagtailcore_locale"')
        ]
        self.assertEqual(standalone_locale_queries, [])

        joined_queries = [
            query
            for query in ctx.captured_queries
            if "wagtailcore_locale" in query["sql"]
        ]
        self.assertEqual(len(joined_queries), 1)

    def test_without_page_renders_no_dropdown(self):
        result = self.render_selector()

        self.assertNotIn("dropdown-toggle", result)


class TestLanguageSelectorCache(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.page = ContentPageFactory(parent=self.home)
        self.url = self.page.url

    @property
    def cache_key(self):
        return language_selector_cache_key(self.page)

    def test_selector_populates_cache(self):
        self.assertIsNone(cache.get(self.cache_key))

        self.client.get(self.url)

        self.assertIsNotNone(cache.get(self.cache_key))

    def test_cached_selector_is_reused(self):
        self.client.get(self.url)
        cache.set(self.cache_key, "cached selector", 60)

        response = self.client.get(self.url)

        self.assertContains(response, "cached selector")

    def test_cached_requests_make_fewer_queries(self):
        self.client.get(self.url)
        with CaptureQueriesContext(connection) as warm:
            self.client.get(self.url)
        cache.delete(self.cache_key)
        with CaptureQueriesContext(connection) as cold:
            self.client.get(self.url)

        self.assertLess(len(warm.captured_queries), len(cold.captured_queries))

    def test_publish_invalidates_cache(self):
        self.client.get(self.url)
        self.page.save_revision().publish()

        self.assertIsNone(cache.get(self.cache_key))

    def test_publishing_a_translation_invalidates_cache(self):
        locale = LocaleFactory(language_code="nl")
        home_translation = self.home.copy_for_translation(locale)
        home_translation.save_revision().publish()

        self.client.get(self.url)
        page_translation = self.page.copy_for_translation(locale)
        page_translation.save_revision().publish()

        self.assertIsNone(cache.get(self.cache_key))

    def test_publishing_unrelated_page_keeps_cache(self):
        other_page = ContentPageFactory(parent=self.home)
        self.client.get(self.url)

        other_page.save_revision().publish()

        self.assertIsNotNone(cache.get(self.cache_key))

    def test_slug_change_invalidates_cache(self):
        self.client.get(self.url)
        with self.captureOnCommitCallbacks(execute=True):
            self.page.slug = "renamed"
            self.page.save()

        self.assertIsNone(cache.get(self.cache_key))

    def test_parent_slug_change_invalidates_child_cache(self):
        child = ContentPageFactory(parent=self.page)
        self.client.get(self.url)
        self.client.get(child.url)
        child_cache_key = language_selector_cache_key(child)

        with self.captureOnCommitCallbacks(execute=True):
            self.page.slug = "renamed"
            self.page.save()

        self.assertIsNone(cache.get(child_cache_key))

    def test_move_invalidates_cache(self):
        other_page = ContentPageFactory(parent=self.home, title="Other page")
        self.client.get(self.url)
        self.page.move(other_page, pos="right")

        self.assertIsNone(cache.get(self.cache_key))

    def test_delete_invalidates_cache(self):
        self.client.get(self.url)
        self.page.delete()

        self.assertIsNone(cache.get(self.cache_key))
