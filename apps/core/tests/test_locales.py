from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.factories import HomePageFactory, LocaleFactory


class TestPageLocales(TestCase):
    def setUp(self):
        self.en = LocaleFactory(language_code="en")
        self.home_page_en = HomePageFactory(locale=self.en)
        self.nl = LocaleFactory(language_code="nl")
        self.home_page_nl = self.home_page_en.copy_for_translation(self.nl)
        self.home_page_nl.save_revision().publish()
        self.user = get_user_model().objects.create_superuser(
            username="admin", password="test"
        )

    def test_can_access_account_settings(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(reverse("wagtailadmin_account"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "简体中文")

    def test_redirect_to_default_language_if_no_translation_available(self):
        # Dutch has content in this test, but is not in LANGUAGES, so Django
        # falls back to the default language and redirects to it.
        language_code = "nl"
        response = self.client.get(
            "/", headers={"accept-language": language_code}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/en/")

    def test_supported_language_without_content_serves_default_language(self):
        # German is in LANGUAGES but has no published content here: Wagtail
        # serves the default-language content under the German URL.
        response = self.client.get("/de/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Wagtail User Guide")
        self.assertEqual(response.headers["Content-Language"], "de")
