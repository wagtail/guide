from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.factories import HomePageFactory, LocaleFactory


class TestPageLocales(TestCase):
    def setUp(self):
        self.en = LocaleFactory(language_code="en")
        self.home_page_en = HomePageFactory(locale=self.en)
        self.nl = LocaleFactory(language_code="nl-4.1.x")
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
        language_code = "de-CH"
        response = self.client.get(
            "/", headers={"accept-language": language_code}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/en/")
