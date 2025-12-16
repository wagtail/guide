from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory, LocaleFactory


class TestAlternateLinkTagsHomePage(TestCase):
    def setUp(self):
        self.en_latest = LocaleFactory(language_code="en-latest")
        self.en_41x = LocaleFactory(language_code="en-4.1.x")
        self.nl_41x = LocaleFactory(language_code="nl-4.1.x")
        self.is_41x = LocaleFactory(language_code="is-4.1.x")

        self.page_en_latest = HomePageFactory(locale=self.en_latest)
        self.page_en_41x = self.page_en_latest.copy_for_translation(self.en_41x)
        self.page_en_41x.save_revision().publish()
        self.page_nl_41x = self.page_en_latest.copy_for_translation(self.nl_41x)
        self.page_nl_41x.save_revision().publish()
        self.page_is_41x = self.page_en_latest.copy_for_translation(self.is_41x)
        self.page_is_41x.save_revision().publish()

    def test_en_latest_no_alternate_tags(self):
        response = self.client.get(self.page_en_latest.full_url)
        # Should not have the alternate tags
        # as there are no translations for the latest version
        self.assertNotContains(response, '<link rel="alternate" hreflang')

    def test_en_41x_alternate_tags(self):
        response = self.client.get(self.page_en_41x.full_url)
        # Should have the alternate tag for the
        # Dutch 4.1.x and Icelandic 4.1.x versions only
        href = self.page_nl_41x.full_url
        self.assertContains(
            response,
            f'<link rel="alternate" hreflang="nl" href="{href}">',
        )
        href = self.page_is_41x.full_url
        self.assertContains(
            response,
            f'<link rel="alternate" hreflang="is" href="{href}">',
        )

        # Should not have the alternate tag for the English latest version
        href = self.page_en_latest.full_url
        self.assertNotContains(
            response,
            f'<link rel="alternate" hreflang="en" href="{href}">',
        )
        self.assertContains(response, '<link rel="alternate" hreflang', count=2)

    def test_nl_41x_alternate_tags(self):
        response = self.client.get(self.page_nl_41x.full_url)
        # Should have the alternate tag for the
        # English 4.1.x and Icelandic 4.1.x versions only
        href = self.page_en_41x.full_url
        self.assertContains(
            response,
            f'<link rel="alternate" hreflang="en" href="{href}">',
        )
        href = self.page_is_41x.full_url
        self.assertContains(
            response,
            f'<link rel="alternate" hreflang="is" href="{href}">',
        )

        # Should not have the alternate tag for the English latest version
        href = self.page_en_latest.full_url
        self.assertNotContains(
            response,
            f'<link rel="alternate" hreflang="en" href="{href}">',
        )
        self.assertContains(response, '<link rel="alternate" hreflang', count=2)


class TestAlternateLinkTagsContentPage(TestAlternateLinkTagsHomePage):
    def setUp(self):
        super().setUp()
        self.page_en_latest = ContentPageFactory(locale=self.en_latest)
        self.page_en_41x = self.page_en_latest.copy_for_translation(self.en_41x)
        self.page_en_41x.save_revision().publish()
        self.page_nl_41x = self.page_en_latest.copy_for_translation(self.nl_41x)
        self.page_nl_41x.save_revision().publish()
        self.page_is_41x = self.page_en_latest.copy_for_translation(self.is_41x)
        self.page_is_41x.save_revision().publish()
