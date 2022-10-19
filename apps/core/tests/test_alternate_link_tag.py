import json

from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory


class TestAlternateLinkTag(TestCase):
    def setUp(self):
        self.en = LocaleFactory(language_code="en-latest")
        self.home_page_en = HomePageFactory(locale=self.en)
        self.nl = LocaleFactory(language_code="nl-4.1.x")
        self.home_page_nl = self.home_page_en.copy_for_translation(self.nl)
        self.home_page_nl.save_revision().publish()
        body = json.dumps(
            [
                {"type": "text", "value": "<p>some test content</p>"},
            ],
        )
        self.content_page_en = ContentPageFactory(body=body, locale=self.en)
        self.content_page_nl = self.content_page_en.copy_for_translation(self.nl)
        self.content_page_nl.save_revision().publish()

    def test_home_page_nl_has_alternate_tag(self):
        response = self.client.get(self.home_page_nl.url)
        self.assertContains(response, '<link rel="alternate" hreflang="en"')

    def test_content_page_nl_has_alternate_tag(self):
        response = self.client.get(self.content_page_nl.url)
        self.assertContains(response, '<link rel="alternate" hreflang="en"')

    def test_home_page_en_has_no_alternate_tag(self):
        response = self.client.get(self.home_page_en.url)
        self.assertNotContains(response, '<link rel="alternate" hreflang="en"')

    def test_content_page_en_has_no_alternate_tag(self):
        response = self.client.get(self.content_page_en.url)
        self.assertNotContains(response, '<link rel="alternate" hreflang="en"')
