from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory


class TestPageResponseStatusCode(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory()
        self.content_page_response = self.client.get(self.content_page.url)
        self.home_page_response = self.client.get(self.home_page.url)

    def test_homepage_response_status_code(self):
        self.assertEqual(self.home_page_response.status_code, 200)

    def test_content_page_response_status_code(self):
        self.assertEqual(self.content_page_response.status_code, 200)

    def test_content_page_content(self):
        self.assertContains(
            self.content_page_response, text="some test content", count=1
        )
        self.assertContains(
            self.content_page_response, text="some more test content", count=1
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
