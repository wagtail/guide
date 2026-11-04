from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import connection
from django.template import Context, Template
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import translation
from wagtail.models import Page, PageViewRestriction

from apps.core.factories import ContentPageFactory, HomePageFactory


class TestHeader(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.a = Page(title="a", slug="a", show_in_menus=True)
        self.home.add_child(instance=self.a)
        self.ab = Page(title="ab", slug="ab", show_in_menus=True)
        self.a.add_child(instance=self.ab)
        self.ac = Page(title="ac", slug="ac", show_in_menus=True)
        self.a.add_child(instance=self.ac)
        self.b = Page(title="b", slug="b", show_in_menus=True)
        self.home.add_child(instance=self.b)

    def test_get_annotated_list_qs(self):
        pages = (
            Page.objects.descendant_of(self.home)
            .filter(depth__gt=2, depth__lte=4)
            .live()
            .in_menu()
        )
        result = Page.get_annotated_list_qs(pages)
        expected = [
            (self.a, {"close": [], "level": 0, "open": True}),
            (self.ab, {"close": [], "level": 1, "open": True}),
            (self.ac, {"close": [0], "level": 1, "open": False}),
            (self.b, {"close": [0], "level": 0, "open": False}),
        ]
        self.assertEqual(result, expected)

    def test_header_inclusion_tag(self):
        # A normal request will go through LocaleMiddleware to activate the locale.
        translation.activate(self.home.locale.language_code)
        template = Template("{% load core_tags %}{% header %}")
        result = template.render(Context({}))
        self.assertIn('aria-label="Wagtail User Guide"', result)
        self.assertIn('<nav class="primary-nav" data-mobile-menu>', result)
        self.assertIn('href="/en/a/"', result)
        self.assertIn('href="/en/a/ab/"', result)
        self.assertIn('href="/en/a/ac/"', result)
        self.assertIn('href="/en/b/"', result)

    def test_header_excludes_private_pages(self):
        private_section = Page(title="members", slug="members", show_in_menus=True)
        self.home.add_child(instance=private_section)

        PageViewRestriction.objects.create(
            page=private_section,
            restriction_type=PageViewRestriction.LOGIN,
        )

        member_page = Page(title="member-only", slug="member-only", show_in_menus=True)
        private_section.add_child(instance=member_page)

        translation.activate(self.home.locale.language_code)
        template = Template("{% load core_tags %}{% header %}")
        result = template.render(Context({}))

        self.assertNotIn('members"', result)


class TestHeaderCache(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.content_page = ContentPageFactory(parent=self.home)
        self.url = self.content_page.url

    @property
    def cache_key(self):
        return make_template_fragment_key("header", ["en"])

    def test_header_populates_cache(self):
        self.assertIsNone(cache.get(self.cache_key))

        self.client.get(self.url)

        self.assertIsNotNone(cache.get(self.cache_key))

    def test_cached_header_is_reused(self):
        self.client.get(self.url)
        cache.set(self.cache_key, "cached header", 60)

        response = self.client.get(self.url)

        self.assertContains(response, "cached header")

    def test_cached_requests_make_fewer_queries(self):
        self.client.get(self.url)
        with CaptureQueriesContext(connection) as warm:
            self.client.get(self.url)
        cache.delete(self.cache_key)
        with CaptureQueriesContext(connection) as cold:
            self.client.get(self.url)

        self.assertLess(len(warm.captured_queries), len(cold.captured_queries))

    def test_active_menu_item_not_rendered_server_side(self):
        response = self.client.get(self.url)

        self.assertNotIn("navigation__link active", response.rendered_content)

    def test_publish_invalidates_cache(self):
        self.client.get(self.url)
        self.content_page.save_revision().publish()

        self.assertIsNone(cache.get(self.cache_key))

    def test_unpublish_invalidates_cache(self):
        self.client.get(self.url)
        self.content_page.unpublish()

        self.assertIsNone(cache.get(self.cache_key))

    def test_delete_invalidates_cache(self):
        self.client.get(self.url)
        self.content_page.delete()

        self.assertIsNone(cache.get(self.cache_key))

    def test_move_invalidates_cache(self):
        other_page = ContentPageFactory(parent=self.home, title="Other page")
        self.client.get(self.url)
        self.content_page.move(other_page, pos="right")

        self.assertIsNone(cache.get(self.cache_key))
