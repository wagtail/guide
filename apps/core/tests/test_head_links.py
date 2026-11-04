import json
from http import HTTPStatus

from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory

# The discovery links every page advertises in its <head>: the API catalog and
# its description (RFC 9727, RFC 8631), plus the agentic discovery documents.
HEAD_LINKS = [
    '<link rel="ard" href="/.well-known/ard.json">',
    '<link rel="ai-catalog" href="/.well-known/ai-catalog.json">',
    '<link rel="api-catalog" href="/.well-known/api-catalog">',
    '<link rel="service-desc" type="application/vnd.oai.openapi+json;version=3.1" '
    'href="/api/v3-preview/openapi.json">',
]


class TestHeadLinks(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory(parent=self.home_page)

    def test_pages_link_to_discovery_documents(self):
        for url in (self.home_page.url, self.content_page.url):
            response = self.client.get(url)
            for link in HEAD_LINKS:
                with self.subTest(url=url, link=link):
                    self.assertContains(response, link)

    def test_ai_catalog_is_served(self):
        response = self.client.get("/.well-known/ai-catalog.json")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_ai_catalog_lists_llms_txt_files(self):
        urls = {entry["url"] for entry in self.get_ai_catalog_entries()}
        self.assertIn("https://guide.wagtail.org/llms.txt", urls)
        self.assertIn("https://guide.wagtail.org/llms-full.txt", urls)

    def test_ai_catalog_lists_the_openapi_description(self):
        openapi = [
            entry
            for entry in self.get_ai_catalog_entries()
            if entry["type"].startswith("application/vnd.oai.")
        ]
        self.assertEqual(len(openapi), 1)
        self.assertEqual(
            openapi[0]["url"],
            "https://guide.wagtail.org/api/v3-preview/openapi.json",
        )
        self.assertEqual(openapi[0]["auth"]["status"], "none")

    def get_ai_catalog_entries(self):
        response = self.client.get("/.well-known/ai-catalog.json")
        content = b"".join(response.streaming_content)
        return json.loads(content)["entries"]
