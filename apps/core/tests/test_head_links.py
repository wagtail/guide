import json

from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory


class TestAICatalogLink(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory(parent=self.home_page)

    def test_pages_link_to_the_ai_catalog(self):
        for url in (self.home_page.url, self.content_page.url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(
                    response,
                    '<link rel="ai-catalog" href="/.well-known/ai-catalog.json">',
                )

    def test_pages_link_to_the_api_catalog(self):
        for url in (self.home_page.url, self.content_page.url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(
                    response,
                    '<link rel="api-catalog" href="/.well-known/api-catalog">',
                )

    def test_pages_link_to_the_api_description(self):
        for url in (self.home_page.url, self.content_page.url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(
                    response,
                    '<link rel="service-desc" '
                    'type="application/vnd.oai.openapi+json;version=3.1" '
                    'href="/api/v3-preview/openapi.json">',
                )

    def test_ai_catalog_is_served(self):
        response = self.client.get("/.well-known/ai-catalog.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_ai_catalog_lists_llms_txt_files(self):
        response = self.client.get("/.well-known/ai-catalog.json")
        content = b"".join(response.streaming_content)
        entries = json.loads(content)["entries"]
        urls = {entry["url"] for entry in entries}
        self.assertIn("https://guide.wagtail.org/llms.txt", urls)
        self.assertIn("https://guide.wagtail.org/llms-full.txt", urls)
