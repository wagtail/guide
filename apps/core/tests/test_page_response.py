import json

from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory


class TestPageResponseStatusCode(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        body = json.dumps(
            [
                {"type": "text", "value": "<p>some test content</p>"},
                {"type": "text", "value": "<p>some more test content</p>"},
            ],
        )
        self.content_page = ContentPageFactory(body=body)
        self.content_page_response = self.client.get(self.content_page.url)
        self.home_page_response = self.client.get(self.home_page.url)

    def test_homepage_response_status_code(self):
        self.assertEqual(self.home_page_response.status_code, 200)

    def test_content_page_response_status_code(self):
        self.assertEqual(self.content_page_response.status_code, 200)

    def test_content_page_content(self):
        self.assertContains(
            self.content_page_response, text="<p>some test content</p>", count=1
        )
        self.assertContains(
            self.content_page_response, text="<p>some more test content</p>", count=1
        )

    def test_content_page_template_used(self):
        self.assertTemplateUsed(
            self.content_page_response, template_name="base.html", count=1
        )
        self.assertTemplateUsed(
            self.content_page_response, template_name="core/content_page.html", count=1
        )
        self.assertTemplateUsed(
            self.content_page_response, template_name="core/blocks/text.html", count=2
        )
