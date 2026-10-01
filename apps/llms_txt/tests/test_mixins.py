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


class TestMarkdownNegotiation(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def get(self, accept=None, path=None):
        headers = {"accept": accept} if accept else {}
        return self.client.get(path or self.content_page.url, headers=headers)

    def test_accept_markdown_returns_markdown(self):
        response = self.get("text/markdown")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertTrue(content.startswith("---\n"))
        self.assertIn(self.content_page.title, content)

    def test_markdown_response_includes_token_estimate(self):
        response = self.get("text/markdown")
        self.assertGreater(int(response["x-markdown-tokens"]), 0)

    def test_markdown_preferred_over_html(self):
        response = self.get("text/markdown, text/html;q=0.9")
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")

    def test_client_order_breaks_quality_ties(self):
        response = self.get("text/markdown, text/html")
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")

    def test_rejected_markdown_returns_html(self):
        response = self.get("text/markdown;q=0, */*")
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_negotiated_markdown_is_not_shared_cacheable(self):
        response = self.get("text/markdown")
        self.assertIn("private", response["Cache-Control"])

    def test_html_is_default(self):
        response = self.get()
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_browser_accept_header_returns_html(self):
        response = self.get(
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        )
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_wildcard_returns_html(self):
        response = self.get("*/*")
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_html_preferred_over_markdown(self):
        response = self.get("text/html, text/markdown;q=0.5")
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_responses_vary_on_accept(self):
        for accept in ("text/markdown", "text/html"):
            with self.subTest(accept=accept):
                response = self.get(accept)
                self.assertIn("Accept", response["Vary"])

    def test_other_routes_are_not_negotiated(self):
        path = self.content_page.url + self.content_page.reverse_subpage("markdown")
        response = self.get("text/html", path=path)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn("x-markdown-tokens", response)
        self.assertNotIn("Accept", response.get("Vary", ""))

    def test_homepage_supports_markdown(self):
        home = self.content_page.get_parent().specific
        response = self.get("text/markdown", path=home.url)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
