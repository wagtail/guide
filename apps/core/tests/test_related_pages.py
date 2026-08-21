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

    def test_related_pages_render_in_curated_order_with_correct_urls(self):
        html = self._get_related_pages_html(self.client.get(self.source.url))

        self.assertLess(
            html.index(self.related_2.title), html.index(self.related_1.title)
        )
        self.assertIn(f'href="{self.related_1.url}"', html)
        self.assertIn(f'href="{self.related_2.url}"', html)

    def test_no_related_pages_section_when_empty(self):
        other_page = ContentPageFactory(parent=self.home, title="Lonely page")
        content = self.client.get(other_page.url).content.decode()

        self.assertNotIn("related-pages", content)

    def test_draft_and_private_pages_are_excluded(self):
        draft = ContentPageFactory(parent=self.home, title="Draft", live=False)
        private = ContentPageFactory(parent=self.home, title="Private")
        PageViewRestriction.objects.create(
            page=private, restriction_type=PageViewRestriction.LOGIN
        )
        RelatedPage.objects.create(
            source_page=self.source, related_page=draft, sort_order=2
        )
        RelatedPage.objects.create(
            source_page=self.source, related_page=private, sort_order=3
        )

        content = self.client.get(self.source.url).content.decode()

        self.assertNotIn("Draft", content)
        self.assertNotIn("Private", content)

    def test_related_pages_appear_in_markdown_export(self):
        markdown = self.source.to_markdown()

        self.assertIn("## Related pages", markdown)
        self.assertIn(f"[{self.related_1.title}]({self.related_1.full_url})", markdown)

    def test_home_page_related_pages_render(self):
        RelatedPage.objects.create(
            source_page=self.home, related_page=self.related_1, sort_order=0
        )

        html = self._get_related_pages_html(self.client.get(self.home.url))

        self.assertIn(self.related_1.title, html)
