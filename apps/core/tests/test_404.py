from http import HTTPStatus

from django.test import TestCase
from wagtail.models import Site

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory

# Unprefixed, so the request is first redirected to the `/en/` URL.
MISSING_PATH = "/some-path-that-does-not-exist"


class TestPageNotFound(TestCase):
    def setUp(self):
        HomePageFactory()

    def test_html_by_default(self):
        response = self.client.get(MISSING_PATH, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
        self.assertIn("Accept", response["Vary"])

    def test_markdown_when_requested(self):
        response = self.client.get(
            MISSING_PATH, headers={"Accept": "text/markdown"}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn("Accept", response["Vary"])
        self.assertIn("private", response["Cache-Control"])
        root_url = Site.objects.get().root_url
        self.assertIn(f"[llms.txt]({root_url}/llms.txt)", response.content.decode())


def create_english_only_page():
    home_en = HomePageFactory(locale=LocaleFactory(language_code="en"))
    page_en = ContentPageFactory(parent=home_en, slug="only-in-english")
    home_de = home_en.copy_for_translation(LocaleFactory(language_code="de"))
    home_de.save_revision().publish()
    return page_en


class TestPageNotFoundFallbackPages(TestCase):
    def setUp(self):
        self.page_en = create_english_only_page()

    def test_html_lists_fallback_pages(self):
        response = self.client.get("/de/only-in-english/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertContains(
            response, self.page_en.url, status_code=HTTPStatus.NOT_FOUND
        )

    def test_markdown_lists_fallback_pages(self):
        response = self.client.get(
            "/de/only-in-english/", headers={"Accept": "text/markdown"}
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(
            f"[{self.page_en.title} - {self.page_en.locale}]({self.page_en.full_url})",
            response.content.decode(),
        )
