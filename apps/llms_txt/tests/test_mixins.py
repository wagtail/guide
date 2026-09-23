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
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertIn(self.content_page.title, content)

    def test_markdown_view_includes_frontmatter(self):
        """The standalone Markdown route leads with a YAML metadata block."""
        response = self.client.get(
            self.content_page.url + self.content_page.reverse_subpage("markdown")
        )
        content = response.content.decode("utf-8")
        self.assertTrue(content.startswith("---\n"))
        self.assertIn(f'title: "{self.content_page.title}"', content)

    def test_to_markdown_omits_frontmatter_by_default(self):
        """
        llms-full.txt concatenates every page, so the embedded form must not
        carry its own `---` block.
        """
        markdown = self.content_page.to_markdown()
        self.assertFalse(markdown.startswith("---"))
        self.assertNotIn("lang:", markdown)
