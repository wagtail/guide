from django.test import TestCase
from wagtail.models import PageViewRestriction

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.core.models import RelatedPage


class TestRelatedPages(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.source = ContentPageFactory(parent=self.home, title="Getting started")
        self.related_1 = ContentPageFactory(parent=self.home, title="How-to guides")
        self.related_2 = ContentPageFactory(parent=self.home, title="Concepts")

        RelatedPage.objects.create(
            source_page=self.source, related_page=self.related_2, sort_order=0
        )
        RelatedPage.objects.create(
            source_page=self.source, related_page=self.related_1, sort_order=1
        )

    def _get_related_pages_html(self, response):
        content = response.content.decode()
        start = content.index('class="related-pages"')
        end = content.index("</div>", start)
        return content[start:end]

    def test_related_pages_render_in_curated_order(self):
        response = self.client.get(self.source.url)
        related_html = self._get_related_pages_html(response)

        concepts_index = related_html.index(self.related_2.title)
        how_to_index = related_html.index(self.related_1.title)
        self.assertLess(concepts_index, how_to_index)

    def test_related_pages_link_to_correct_urls(self):
        response = self.client.get(self.source.url)
        related_html = self._get_related_pages_html(response)

        self.assertIn(f'href="{self.related_1.url}"', related_html)
        self.assertIn(f'href="{self.related_2.url}"', related_html)

    def test_no_related_pages_section_when_empty(self):
        other_page = ContentPageFactory(parent=self.home, title="Lonely page")
        response = self.client.get(other_page.url)
        content = response.content.decode()

        self.assertNotIn("related-pages", content)

    def test_draft_related_pages_are_excluded(self):
        draft_page = ContentPageFactory(
            parent=self.home, title="Draft page", live=False
        )
        RelatedPage.objects.create(
            source_page=self.source, related_page=draft_page, sort_order=2
        )

        response = self.client.get(self.source.url)
        content = response.content.decode()

        self.assertNotIn(draft_page.title, content)

    def test_private_related_pages_are_excluded(self):
        private_page = ContentPageFactory(parent=self.home, title="Private page")
        PageViewRestriction.objects.create(
            page=private_page,
            restriction_type=PageViewRestriction.LOGIN,
        )
        RelatedPage.objects.create(
            source_page=self.source, related_page=private_page, sort_order=2
        )

        response = self.client.get(self.source.url)
        content = response.content.decode()

        self.assertNotIn(private_page.title, content)

    def test_related_pages_appear_in_markdown_export(self):
        markdown = self.source.to_markdown()

        self.assertIn("## Related pages", markdown)
        self.assertIn(f"[{self.related_1.title}]({self.related_1.full_url})", markdown)
        self.assertIn(f"[{self.related_2.title}]({self.related_2.full_url})", markdown)

    def test_no_related_pages_heading_in_markdown_when_empty(self):
        other_page = ContentPageFactory(parent=self.home, title="Lonely page")
        markdown = other_page.to_markdown()

        self.assertNotIn("## Related pages", markdown)

    def test_home_page_related_pages_render(self):
        RelatedPage.objects.create(
            source_page=self.home, related_page=self.related_1, sort_order=0
        )

        response = self.client.get(self.home.url)
        related_html = self._get_related_pages_html(response)

        self.assertIn(self.related_1.title, related_html)
