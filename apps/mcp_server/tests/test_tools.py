from django.test import TestCase
from wagtail.models import PageViewRestriction

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory
from apps.core.tests.test_404 import create_english_only_page

from .test_views import MCPTestMixin


def get_text(result):
    return result["content"][0]["text"]


class TestSearchDocs(MCPTestMixin, TestCase):
    def setUp(self):
        self.home_en = HomePageFactory(locale=LocaleFactory(language_code="en"))
        self.page_en = ContentPageFactory(parent=self.home_en, title="Streamfield")
        self.home_fr = self.home_en.copy_for_translation(
            LocaleFactory(language_code="fr")
        )
        self.home_fr.save_revision().publish()

    def search(self, **arguments):
        return self.call_tool("search_docs", arguments)

    def test_returns_page_details(self):
        result = self.search(query="streamfield")
        self.assertFalse(result["isError"])
        [page] = result["structuredContent"]["result"]
        self.assertEqual(
            page,
            {
                "title": "Streamfield",
                "search_description": "",
                "full_url": self.page_en.full_url,
                "parent_section": "Home",
            },
        )

    def test_default_limit(self):
        for number in range(6):
            ContentPageFactory(parent=self.home_en, title=f"Streamfield {number}")
        result = self.search(query="streamfield")
        self.assertEqual(len(result["structuredContent"]["result"]), 5)

    def test_limit(self):
        for number in range(3):
            ContentPageFactory(parent=self.home_en, title=f"Streamfield {number}")
        result = self.search(query="streamfield", limit=2)
        self.assertEqual(len(result["structuredContent"]["result"]), 2)

    def test_locale(self):
        page_fr = ContentPageFactory(
            parent=self.home_fr, locale=self.home_fr.locale, title="Streamfield"
        )
        result = self.search(query="streamfield", locale="fr")
        [page] = result["structuredContent"]["result"]
        self.assertEqual(page["full_url"], page_fr.full_url)

    def test_unknown_locale(self):
        result = self.search(query="streamfield", locale="xx")
        self.assertTrue(result["isError"])
        self.assertIn("Unknown locale 'xx'. Available: en, fr.", get_text(result))


class TestFetchDocsPage(MCPTestMixin, TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.page = ContentPageFactory(parent=self.home, title="Writing")

    def fetch(self, url):
        return self.call_tool("fetch_docs_page", {"url": url})

    def test_urls(self):
        for url in (
            self.page.full_url,
            self.page.url,
            self.page.full_url + self.page.reverse_subpage("markdown"),
        ):
            with self.subTest(url=url):
                result = self.fetch(url)
                self.assertFalse(result["isError"])
                self.assertNotIn("structuredContent", result)
                markdown = get_text(result)
                self.assertTrue(markdown.startswith("---\ntitle:"))
                self.assertIn("# Writing", markdown)
                self.assertIn(f"Page URL: {self.page.full_url}", markdown)

    def test_slug_ending_in_markdown(self):
        page = ContentPageFactory(parent=self.home, slug="using-markdown")
        result = self.fetch(page.url)
        self.assertFalse(result["isError"])
        self.assertIn(f"Page URL: {page.full_url}", get_text(result))

    def test_home_page(self):
        result = self.fetch(self.home.full_url)
        self.assertFalse(result["isError"])
        self.assertIn(f"Page URL: {self.home.full_url}", get_text(result))

    def test_other_site(self):
        result = self.fetch(f"https://example.com{self.page.url}")
        self.assertTrue(result["isError"])
        self.assertIn("is not a page of this site", get_text(result))

    def test_missing_page(self):
        result = self.fetch("/en/missing/")
        self.assertTrue(result["isError"])
        self.assertIn("No page found at /en/missing/.", get_text(result))

    def test_draft_page(self):
        self.page.unpublish()
        result = self.fetch(self.page.full_url)
        self.assertTrue(result["isError"])

    def test_private_page(self):
        PageViewRestriction.objects.create(
            page=self.page,
            restriction_type=PageViewRestriction.PASSWORD,
            password="secret",  # pragma: allowlist secret
        )
        result = self.fetch(self.page.full_url)
        self.assertTrue(result["isError"])
        self.assertNotIn("# Writing", get_text(result))


class TestFetchDocsPageFallback(MCPTestMixin, TestCase):
    def test_lists_pages_in_other_languages(self):
        page_en = create_english_only_page()
        result = self.call_tool("fetch_docs_page", {"url": "/de/only-in-english/"})
        self.assertTrue(result["isError"])
        self.assertIn(
            f"It exists in other languages: {page_en.full_url}", get_text(result)
        )
