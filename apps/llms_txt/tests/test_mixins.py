from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory


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

    def test_negotiated_markdown_is_not_shared_cacheable(self):
        response = self.get("text/markdown")
        self.assertIn("private", response["Cache-Control"])

    def test_html_is_default(self):
        response = self.get()
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


class TestMarkdownFromHtml(TestCase):
    """
    Page Markdown responses are converted from the page's rendered HTML, so
    agents see what visitors see around the content.
    """

    def setUp(self):
        self.home_page = HomePageFactory()
        self.section = ContentPageFactory(parent=self.home_page, title="Releases")
        self.child = ContentPageFactory(parent=self.section, title="New in Wagtail 8.1")
        self.menu_page = ContentPageFactory(
            parent=self.home_page, title="Manage images", show_in_menus=True
        )

    def get_markdown(self, page):
        response = self.client.get(page.url, headers={"accept": "text/markdown"})
        return response.content.decode()

    def test_section_pages_list_their_pages(self):
        markdown = self.get_markdown(self.section)
        self.assertIn("## In this section", markdown)
        self.assertIn(f"[New in Wagtail 8.1]({self.child.full_url})", markdown)

    def test_links_to_llms_txt(self):
        markdown = self.get_markdown(self.section)
        self.assertIn("[View llms.txt](http://localhost/llms.txt)", markdown)

    def test_keeps_the_header(self):
        markdown = self.get_markdown(self.section)
        self.assertTrue(markdown.startswith("---\n"))
        self.assertIn(f"Page URL: {self.section.full_url}", markdown)

    def test_leaves_out_the_feedback_form(self):
        markdown = self.get_markdown(self.section)
        self.assertNotIn("Was this page helpful?", markdown)

    def test_leaves_out_the_menu(self):
        html = self.client.get(self.section.url).content.decode()
        self.assertIn(f'href="{self.menu_page.url}"', html)
        markdown = self.get_markdown(self.section)
        self.assertNotIn(self.menu_page.full_url, markdown)

    def test_to_markdown_is_unchanged(self):
        """llms-full.txt and the MCP server keep using the page's content only."""
        markdown = self.section.to_markdown()
        self.assertNotIn("In this section", markdown)
        self.assertNotIn("llms.txt", markdown)
