from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.factories import HomePageFactory, LocaleFactory


class TestPageLocales(TestCase):
    def setUp(self):
        self.en = LocaleFactory(language_code="en-latest")
        self.home_page_en = HomePageFactory(locale=self.en)
        self.nl = LocaleFactory(language_code="nl-4.1.x")
        self.home_page_nl = self.home_page_en.copy_for_translation(self.nl)
        self.home_page_nl.save_revision().publish()
        self.user = get_user_model().objects.create_superuser(
            username="admin", password="test"
        )

    def test_language_code_in_settings_languages(self):
        language_codes = [key for key, _ in settings.LANGUAGES]
        self.assertIn("en-latest", language_codes)
        self.assertIn("nl-4.1.x", language_codes)

    def test_url_language_prefix_can_contain_dots(self):
        self.assertEqual(self.home_page_en.url, "/en-latest/")
        response = self.client.get(self.home_page_en.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.home_page_nl.url, "/nl-4.1.x/")
        response = self.client.get(self.home_page_nl.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_can_access_account_settings(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(reverse("wagtailadmin_account"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "简体中文")

    def test_redirect_to_default_language_if_no_translation_available(self):
        language_code = "de-CH"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=language_code, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/en-latest/")
