import unittest
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Site

from apps.core.factories import ContentPageFactory, HomePageFactory

skip_if_markdown_disabled = unittest.skipUnless(
    settings.PAGE_MARKDOWN_ENABLED, "page Markdown is disabled"
)


class TestMarkdownRouteMixin(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    @skip_if_markdown_disabled
    def test_has_markdown_route_property(self):
        self.assertTrue(self.content_page.has_markdown_route)

    def test_to_markdown_includes_page_url(self):
        """Test that to_markdown includes the page URL."""
        markdown = self.content_page.to_markdown()
        self.assertIn("Page URL:", markdown)

    @skip_if_markdown_disabled
    def test_markdown_view_route_accessible(self):
        """Test that the markdown route is accessible via URL."""
        response = self.client.get(
            self.content_page.url + self.content_page.reverse_subpage("markdown")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertIn(self.content_page.title, content)

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
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
    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
    def test_accept_markdown_returns_markdown(self):
        response = self.get("text/markdown")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertTrue(content.startswith("---\n"))
        self.assertIn(self.content_page.title, content)

    @skip_if_markdown_disabled
    def test_markdown_response_includes_token_estimate(self):
        response = self.get("text/markdown")
        self.assertGreater(int(response["x-markdown-tokens"]), 0)

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
    def test_other_routes_are_not_negotiated(self):
        path = self.content_page.url + self.content_page.reverse_subpage("markdown")
        response = self.get("text/html", path=path)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn("x-markdown-tokens", response)
        self.assertNotIn("Accept", response.get("Vary", ""))

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
    def test_section_pages_list_their_pages(self):
        markdown = self.get_markdown(self.section)
        self.assertIn("## In this section", markdown)
        self.assertIn(f"[New in Wagtail 8.1]({self.child.full_url})", markdown)

    @skip_if_markdown_disabled
    def test_leaves_out_page_tools(self):
        markdown = self.get_markdown(self.section)
        site = self.section.get_site()
        self.assertNotIn("View page Markdown", markdown)
        self.assertNotIn("View llms.txt", markdown)
        # The documentation index callout still links to llms.txt.
        self.assertIn(f"{site.root_url}/llms.txt", markdown)

    @skip_if_markdown_disabled
    def test_explicit_route_matches_negotiated_markdown(self):
        response = self.client.get(
            self.section.url + self.section.reverse_subpage("markdown")
        )
        self.assertEqual(response.content.decode(), self.get_markdown(self.section))

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
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

    @skip_if_markdown_disabled
    def test_keeps_the_header(self):
        markdown = self.get_markdown(self.section)
        self.assertTrue(markdown.startswith("---\n"))
        self.assertIn(f"Page URL: {self.section.full_url}", markdown)

    @skip_if_markdown_disabled
    def test_leaves_out_the_feedback_form(self):
        markdown = self.get_markdown(self.section)
        self.assertNotIn("Was this page helpful?", markdown)

    @skip_if_markdown_disabled
    def test_leaves_out_the_theme_labels(self):
        markdown = self.get_markdown(self.section)
        self.assertNotIn("Dark", markdown)
        self.assertNotIn("Light", markdown)

    @skip_if_markdown_disabled
    def test_leaves_out_the_menu(self):
        html = self.client.get(self.section.url).content.decode()
        self.assertIn(f'href="{self.menu_page.url}"', html)
        markdown = self.get_markdown(self.section)
        # The menu's page is still in the site sitemap, but its label is not.
        self.assertNotIn(f"Manage images]({self.menu_page.full_url})", markdown)

    def test_to_markdown_is_unchanged(self):
        """llms-full.txt and the MCP server keep using the page's content only."""
        markdown = self.section.to_markdown()
        self.assertNotIn("In this section", markdown)
        self.assertNotIn("llms.txt", markdown)

    def sitemap_lines(self, markdown):
        return [
            line
            for line in markdown.split("\n## Site Map\n")[1].splitlines()
            if line.lstrip().startswith("- ")
        ]

    @staticmethod
    def page_link(page):
        return f"[{page.title}]({page.full_url}{page.reverse_subpage('markdown')})"

    @skip_if_markdown_disabled
    def test_appends_site_sitemap(self):
        markdown = self.get_markdown(self.section)
        self.assertIn("\n## Site Map\n", markdown)
        self.assertLess(
            markdown.index("## In this section"), markdown.index("## Site Map")
        )
        self.assertIn(
            f"        - {self.page_link(self.child)}",
            self.sitemap_lines(markdown),
        )

    @skip_if_markdown_disabled
    def test_site_sitemap_is_nested_by_page_depth(self):
        # Each page is a list item, nested under its parent, with a 4-space
        # indent per level of the page tree. The site root is the top item.
        markdown = self.get_markdown(self.home_page)
        self.assertEqual(
            self.sitemap_lines(markdown),
            [
                f"    - {self.page_link(self.section)}",
                f"        - {self.page_link(self.child)}",
                f"    - {self.page_link(self.menu_page)}",
            ],
        )

    @skip_if_markdown_disabled
    def test_site_sitemap_matches_llms_txt_table_of_contents(self):
        """
        The sitemap is the llms.txt table of contents, so both stay in sync
        and neither lists the page that the agent is already reading.
        """
        markdown = self.get_markdown(self.section)
        llms_txt = self.client.get("/llms.txt").content.decode()
        toc = llms_txt.split("## Table of Contents\n")[1].split("\n## Optional")[0]
        # Both link to every page in sitemap order, with the same nesting, which
        # is absolute: leaving out the section page must not shift its child.
        expected = [
            line
            for line in toc.splitlines()
            if line.lstrip().startswith("- ")
            and self.page_link(self.section) not in line
        ]
        self.assertEqual(self.sitemap_lines(markdown), expected)

    @skip_if_markdown_disabled
    def test_homepage_sitemap_lists_every_page_but_itself(self):
        markdown = self.get_markdown(self.home_page)
        self.assertIn(
            f"    - {self.page_link(self.section)}",
            self.sitemap_lines(markdown),
        )
        self.assertNotIn(reverse("llms_txt"), markdown.split("## Site Map\n")[1])


@override_settings(PAGE_MARKDOWN_ENABLED=False)
class TestPageMarkdownDisabled(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory(parent=self.home_page)

    def test_pages_have_no_markdown_route(self):
        self.assertFalse(self.content_page.has_markdown_route)

    def test_markdown_route_is_not_found(self):
        response = self.client.get(
            self.content_page.url + self.content_page.reverse_subpage("markdown")
        )
        self.assertEqual(response.status_code, 404)

    def test_markdown_is_not_negotiated(self):
        response = self.client.get(
            self.content_page.url, headers={"accept": "text/markdown"}
        )
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_cached_paths_leave_out_markdown_route(self):
        self.assertNotIn("/markdown/", self.content_page.get_cached_paths())

    def test_page_links_to_itself_not_markdown(self):
        html = self.client.get(self.content_page.url).content.decode()
        self.assertNotIn('type="text/markdown;charset=utf-8"', html)
        self.assertNotIn("View page Markdown", html)

    def test_llms_txt_links_to_pages_not_markdown(self):
        llms_txt = self.client.get("/llms.txt").content.decode()
        self.assertIn(f"]({self.content_page.full_url})", llms_txt)
        self.assertNotIn("/markdown/)", llms_txt)

    def test_llms_txt_and_llms_full_txt_are_unaffected(self):
        self.assertEqual(self.client.get("/llms.txt").status_code, 200)
        full = self.client.get("/llms-full.txt")
        self.assertEqual(full.status_code, 200)
        self.assertIn(self.content_page.title, full.content.decode())
