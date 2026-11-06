import json
import uuid

from django.core.cache import cache
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from apps.core.factories import ContentPageFactory, HomePageFactory

# Production uses Redis, so cache reads and writes aren't database queries
# there. Use an in-memory cache so the counts only reflect page rendering.
LOCMEM_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}


@override_settings(CACHES=LOCMEM_CACHES)
class TestPageQueryCounts(TestCase):
    def setUp(self):
        cache.clear()
        self.home = HomePageFactory()
        self.page = ContentPageFactory(parent=self.home)

    def get_query_count(self, url):
        # Start from an empty cache so the cached header and language
        # selector fragments are rendered too.
        cache.clear()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(ctx.captured_queries)

    def set_home_sections(self, pages):
        self.home.sections = json.dumps(
            [
                {
                    "type": "section_grid",
                    "value": [
                        {
                            "type": "item",
                            "id": str(uuid.uuid4()),
                            "value": {
                                "section": "tutorial",
                                "title": page.title,
                                "text": "Section text",
                                "page": page.pk,
                            },
                        }
                        for page in pages
                    ],
                }
            ]
        )
        self.home.save_revision().publish()

    def test_content_page(self):
        # Warm the cached fragments, as for most requests in production.
        self.client.get(self.page.url)
        with self.assertNumQueries(17):
            self.client.get(self.page.url)

    def test_home_page(self):
        self.set_home_sections([self.page])
        self.client.get(self.home.url)
        with self.assertNumQueries(12):
            self.client.get(self.home.url)

    def test_child_pages_do_not_add_queries(self):
        ContentPageFactory(parent=self.page)
        expected = self.get_query_count(self.page.url)

        for _ in range(4):
            ContentPageFactory(parent=self.page)

        self.assertEqual(self.get_query_count(self.page.url), expected)

    def test_menu_pages_do_not_add_queries(self):
        ContentPageFactory(parent=self.home)
        expected = self.get_query_count(self.page.url)

        for _ in range(4):
            section = ContentPageFactory(parent=self.home)
            ContentPageFactory(parent=section)

        self.assertEqual(self.get_query_count(self.page.url), expected)

    def test_home_page_sections_do_not_add_queries(self):
        pages = [ContentPageFactory(parent=self.home) for _ in range(5)]
        self.set_home_sections(pages[:1])
        expected = self.get_query_count(self.home.url)

        self.set_home_sections(pages)

        self.assertEqual(self.get_query_count(self.home.url), expected)
