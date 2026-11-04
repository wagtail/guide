from django.test import TestCase
from wagtail.models import Page

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory


class TestHreflangs(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        # Slugs are localised: the English and French pages have different slugs.
        self.en_page = ContentPageFactory(parent=self.home, slug="getting-started")
        self.fr_locale = LocaleFactory(language_code="fr")
        self.fr_home = self.home.copy_for_translation(self.fr_locale)
        self.fr_home.save_revision().publish()
        self.fr_page = self.en_page.copy_for_translation(self.fr_locale)
        self.fr_page.slug = "commencement"
        self.fr_page.save()
        self.fr_page.save_revision().publish()

    def get_hreflangs(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return [
            line.strip()
            for line in response.rendered_content.splitlines()
            if line.strip().startswith("<link")
            and ("hreflang" in line or 'rel="canonical"' in line)
        ]

    def test_english_page_links_use_localised_slugs(self):
        lines = self.get_hreflangs(self.en_page.url)

        self.assertIn(
            f'<link rel="alternate" hreflang="en" href="{self.en_page.full_url}">',
            lines,
        )
        self.assertIn(
            f'<link rel="alternate" hreflang="fr" href="{self.fr_page.full_url}">',
            lines,
        )

    def test_french_page_links_use_localised_slugs(self):
        lines = self.get_hreflangs(self.fr_page.url)

        self.assertIn(
            f'<link rel="alternate" hreflang="en" href="{self.en_page.full_url}">',
            lines,
        )
        self.assertIn(
            f'<link rel="alternate" hreflang="fr" href="{self.fr_page.full_url}">',
            lines,
        )

    def test_english_page_lists_itself(self):
        lines = self.get_hreflangs(self.en_page.url)

        self.assertIn(
            f'<link rel="alternate" hreflang="en" href="{self.en_page.full_url}">',
            lines,
        )

    def test_french_page_lists_itself(self):
        lines = self.get_hreflangs(self.fr_page.url)

        self.assertIn(
            f'<link rel="alternate" hreflang="fr" href="{self.fr_page.full_url}">',
            lines,
        )

    def test_canonical_is_self_referential(self):
        for page in (self.en_page, self.fr_page):
            lines = self.get_hreflangs(page.url)

            self.assertIn(
                f'<link rel="canonical" href="{page.full_url}">',
                lines,
            )

    def test_x_default_points_to_english(self):
        for page in (self.en_page, self.fr_page):
            lines = self.get_hreflangs(page.url)

            self.assertIn(
                f'<link rel="alternate" hreflang="x-default" '
                f'href="{self.en_page.full_url}">',
                lines,
            )

    def test_unpublished_translation_is_omitted(self):
        # A translation that was never published must not appear as an alternate.
        de_locale = LocaleFactory(language_code="de")
        de_home = self.home.copy_for_translation(de_locale)
        de_home.save_revision().publish()
        de_page = self.en_page.copy_for_translation(de_locale)
        de_page.slug = "erste-schritte"
        de_page.save()

        lines = self.get_hreflangs(self.en_page.url)

        self.assertNotIn("erste-schritte", "\n".join(lines))
        self.assertIn(
            f'<link rel="alternate" hreflang="en" href="{self.en_page.full_url}">',
            lines,
        )

    def test_translation_without_url_is_omitted(self):
        # A translation can be live and public yet have no URL (full_url is
        # None) when it isn't reachable through a site. It must be omitted
        # rather than rendered with a literal href="None".
        ar_locale = LocaleFactory(language_code="ar")
        ar_home = self.home.copy_for_translation(ar_locale)
        ar_home.save_revision().publish()
        ar_page = self.en_page.copy_for_translation(ar_locale)
        ar_page.slug = "al-bidaya"
        ar_page.save()
        ar_page.save_revision().publish()

        # Move the live, public translation out from under the site root so it
        # resolves to no URL, while staying live.
        root = Page.get_first_root_node()
        ar_page.move(root, pos="last-child")
        ar_page.refresh_from_db()
        self.assertIsNone(ar_page.full_url)
        self.assertTrue(ar_page.live)

        lines = self.get_hreflangs(self.en_page.url)

        self.assertNotIn('href="None"', "\n".join(lines))
        self.assertNotIn('hreflang="ar"', "\n".join(lines))
        self.assertIn(
            f'<link rel="alternate" hreflang="en" href="{self.en_page.full_url}">',
            lines,
        )
        self.assertIn(
            f'<link rel="alternate" hreflang="x-default" '
            f'href="{self.en_page.full_url}">',
            lines,
        )
