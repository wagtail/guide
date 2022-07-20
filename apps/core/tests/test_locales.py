from http import HTTPStatus

from django.conf import settings
from django.test import TestCase

from apps.core.factories import HomePageFactory, LocaleFactory


class TestPageLocales(TestCase):
    def setUp(self):
        self.en = LocaleFactory(language_code="en-latest")
        self.home_page_en = HomePageFactory(locale=self.en)
        self.nl = LocaleFactory(language_code="nl-3.1.x")
        self.home_page_nl = self.home_page_en.copy_for_translation(self.nl)
        self.home_page_nl.save_revision().publish()

    def test_language_code_in_settings_languages(self):
        language_codes = [key for key, _ in settings.LANGUAGES]
        self.assertIn("en-latest", language_codes)
        self.assertIn("nl-3.1.x", language_codes)

    def test_url_language_prefix_can_contain_dots(self):
        self.assertEqual(self.home_page_en.url, "/en-latest/")
        response = self.client.get(self.home_page_en.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.home_page_nl.url, "/nl-3.1.x/")
        response = self.client.get(self.home_page_nl.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
