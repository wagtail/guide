from django.core.cache import cache
from django.test import TestCase
from wagtail.models import Site

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.llms_txt.views import (
    LLMS_FULL_TXT_TEMPLATE,
    LLMS_TXT_TEMPLATE,
    get_cache_key,
)


class TestLLMsTxtViews(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory(parent=self.home_page)
        self.site = Site.objects.get(is_default_site=True)

    def cache_key(self, template_name):
        return get_cache_key(self.site.pk, template_name)

    def test_llms_txt_renders_pages(self):
        response = self.client.get("/llms.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn(self.content_page.title.encode(), response.content)

    def test_llms_full_txt_renders_pages(self):
        response = self.client.get("/llms-full.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn(self.content_page.title.encode(), response.content)

    def test_responses_are_cached(self):
        for path, template_name in (
            ("/llms.txt", LLMS_TXT_TEMPLATE),
            ("/llms-full.txt", LLMS_FULL_TXT_TEMPLATE),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIsNotNone(cache.get(self.cache_key(template_name)))

    def test_cached_response_is_reused(self):
        self.client.get("/llms-full.txt")
        cache.set(self.cache_key(LLMS_FULL_TXT_TEMPLATE), "cached content", 60)

        response = self.client.get("/llms-full.txt")

        self.assertIn(b"cached content", response.content)

    def test_publish_invalidates_cache(self):
        self.client.get("/llms-full.txt")
        self.content_page.save_revision().publish()

        self.assertIsNone(cache.get(self.cache_key(LLMS_FULL_TXT_TEMPLATE)))
        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))

    def test_unpublish_invalidates_cache(self):
        self.client.get("/llms.txt")
        self.content_page.unpublish()

        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))

    def test_delete_invalidates_cache(self):
        self.client.get("/llms.txt")
        self.content_page.delete()

        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))

    def test_move_invalidates_cache(self):
        second_page = ContentPageFactory(parent=self.home_page, title="Second page")
        self.client.get("/llms.txt")
        self.content_page.move(second_page, pos="right")

        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))
