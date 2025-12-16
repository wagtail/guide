from django.test import TestCase

from apps.core.factories import ContentPageFactory


class TestMarkdownRouteMixin(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_has_markdown_route_property(self):
        self.assertTrue(self.content_page.has_markdown_route)

    def test_to_markdown_includes_page_url(self):
        """Test that to_markdown includes the page URL."""
        markdown = self.content_page.to_markdown()
        self.assertIn("Page URL:", markdown)

    def test_markdown_view_route_accessible(self):
        """Test that the markdown route is accessible via URL."""
        response = self.client.get(
            self.content_page.url + self.content_page.reverse_subpage("markdown")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown; charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertIn(self.content_page.title, content)
