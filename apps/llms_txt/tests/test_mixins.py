from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Site

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

    def test_to_markdown_points_to_documentation_index(self):
        markdown = self.content_page.to_markdown(frontmatter=True)
        site = Site.objects.get(is_default_site=True)
        self.assertIn(
            "---\n"
            "> Documentation Index\n"
            f"> Fetch the complete documentation index at: {site.root_url}"
            f"{reverse('llms_txt')}\n"
            "> Use this file to discover all available pages before exploring "
            "further.\n"
            "\n"
            f"# {self.content_page.title}\n",
            markdown,
        )

    def test_to_markdown_index_url_without_request(self):
        """
        Callers that render pages without a request (llms-full.txt, the MCP
        server) must still link to the full llms.txt URL, not a bare path.
        """
        markdown = self.content_page.to_markdown(frontmatter=True)
        site = Site.objects.get(is_default_site=True)
        self.assertIn(
            f"> Fetch the complete documentation index at: {site.root_url}"
            f"{reverse('llms_txt')}\n",
            markdown,
        )

    def test_markdown_response_points_to_documentation_index(self):
        response = self.client.get(
            self.content_page.url + self.content_page.reverse_subpage("markdown")
        )
        content = response.content.decode("utf-8")
        self.assertIn("> Documentation Index\n", content)
        # The metadata precedes the converted HTML, including the page heading.
        self.assertLess(content.index("> Documentation Index"), content.index("\n# "))
        self.assertLess(
            content.index("> Documentation Index"), content.index("Page URL:")
        )
        self.assertLess(content.index("Page URL:"), content.index("\n# "))

    def test_llms_full_txt_omits_documentation_index(self):
        """The index callout would be wrong in llms-full.txt: llms.txt already
        contains it, referenced as the table of contents."""
        response = self.client.get("/llms-full.txt")
        self.assertNotIn(b"> Documentation Index", response.content)


class TestMarkdownFrontendCachePurging(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_get_cached_paths_includes_markdown_route(self):
        paths = self.content_page.get_cached_paths()
        self.assertIn("/", paths)
        self.assertIn("/markdown/", paths)

    @override_settings(
        WAGTAILFRONTENDCACHE={
            "default": {
                "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
                "ZONEID": "test-zone",
                "BEARER_TOKEN": "test-token",
            }
        }
    )
    def test_publishing_purges_the_markdown_url(self):
        """
        Wagtail's frontend cache handler purges every cached path on publish,
        which now includes the markdown route.
        """
        markdown_url = self.content_page.full_url + self.content_page.reverse_subpage(
            "markdown"
        )
        with mock.patch(
            "wagtail.contrib.frontend_cache.backends.CloudflareBackend.purge_batch"
        ) as purge_batch:
            self.content_page.save_revision().publish()

        purged_urls = {
            url for call in purge_batch.call_args_list for url in call.args[0]
        }
        self.assertIn(markdown_url, purged_urls)


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
        for accept in (
            None,
            "*/*",
            "text/*",
            "application/json",
            "text/html, text/markdown;q=0.5",
            "text/markdown;q=0, */*",
        ):
            with self.subTest(accept=accept):
                response = self.get(accept)
                self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_markdown_preferences(self):
        for accept in (
            "text/markdown, text/html;q=0.9",
            "text/markdown, text/html",
        ):
            with self.subTest(accept=accept):
                response = self.get(accept)
                self.assertEqual(
                    response["Content-Type"], "text/markdown;charset=utf-8"
                )

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

    def test_leaves_out_page_tools(self):
        markdown = self.get_markdown(self.section)
        site = self.section.get_site()
        self.assertNotIn("View page Markdown", markdown)
        self.assertNotIn("View llms.txt", markdown)
        # The documentation index callout still links to llms.txt.
        self.assertIn(f"{site.root_url}/llms.txt", markdown)

    def test_explicit_route_matches_negotiated_markdown(self):
        response = self.client.get(
            self.section.url + self.section.reverse_subpage("markdown")
        )
        self.assertEqual(response.content.decode(), self.get_markdown(self.section))

    def test_homepage_includes_introduction_and_sections(self):
        self.home_page.introduction = "<p>Welcome to the guide.</p>"
        self.home_page.sections = [
            (
                "section_grid",
                [
                    {
                        "section": "reference",
                        "title": "Explore releases",
                        "text": "Changes in each Wagtail version.",
                        "page": self.section,
                    }
                ],
            )
        ]
        self.home_page.save()
        markdown = self.get_markdown(self.home_page)
        self.assertIn("Welcome to the guide.", markdown)
        self.assertIn(f"[Explore releases]({self.section.full_url})", markdown)
        self.assertIn("Changes in each Wagtail version.", markdown)

    def test_body_preserves_annotations_alerts_and_absolute_links(self):
        self.section.body = [
            (
                "text_annotated",
                {
                    "version": "8.1",
                    "change_type": "added",
                    "content": '<p>Read <a href="details/">the details</a>.</p>',
                },
            ),
            ("alert", {"alert_type": "Warning", "alert_body": "<p>Save first.</p>"}),
        ]
        self.section.save()
        markdown = self.get_markdown(self.section)
        self.assertIn("Added in Wagtail 8.1", markdown)
        self.assertIn(f"[the details]({self.section.full_url}details/)", markdown)
        self.assertIn("Warning", markdown)
        self.assertIn("Save first.", markdown)

    def test_keeps_the_header(self):
        markdown = self.get_markdown(self.section)
        self.assertTrue(markdown.startswith("---\n"))
        self.assertIn(f"Page URL: {self.section.full_url}", markdown)

    def test_leaves_out_the_feedback_form(self):
        markdown = self.get_markdown(self.section)
        self.assertNotIn("Was this page helpful?", markdown)

    def test_leaves_out_the_theme_labels(self):
        markdown = self.get_markdown(self.section)
        self.assertNotIn("Dark", markdown)
        self.assertNotIn("Light", markdown)

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
