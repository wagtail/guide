import json

from django.template import engines
from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory

TITLE = "Bread & Butter <3"
DESCRIPTION = 'If you\'re new to Wagtail, read "Getting started" first.'


class TestMarkdownIsNotHtmlEscaped(TestCase):
    """
    Markdown and plain text templates must output text as is, not HTML
    entities such as `&#39;` or `&amp;`.
    """

    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory(
            parent=self.home_page, title=TITLE, search_description=DESCRIPTION
        )

    def assertNotEscaped(self, content):
        self.assertIn(TITLE, content)
        self.assertIn(DESCRIPTION, content)
        for entity in ("&amp;", "&lt;", "&#39;", "&#34;", "&quot;"):
            self.assertNotIn(entity, content)

    def test_page_markdown(self):
        response = self.client.get(
            self.content_page.url, headers={"accept": "text/markdown"}
        )
        self.assertNotEscaped(response.content.decode())

    def test_llms_txt(self):
        response = self.client.get("/llms.txt")
        self.assertIn(f"[{TITLE}]", response.content.decode())

    def test_llms_full_txt(self):
        response = self.client.get("/llms-full.txt")
        self.assertNotEscaped(response.content.decode())

    def test_frontmatter_is_still_valid_json(self):
        content = self.content_page.to_markdown(frontmatter=True)
        title_line = next(
            line for line in content.splitlines() if line.startswith("title: ")
        )
        self.assertEqual(json.loads(title_line.removeprefix("title: ")), TITLE)


class TestAutoescapeSelection(TestCase):
    def setUp(self):
        self.autoescape = engines["jinja2"].env.autoescape

    def test_markdown_and_text_templates_are_not_escaped(self):
        for name in ("llms_txt/page.md.jinja", "llms_txt/llms.txt.jinja"):
            with self.subTest(name=name):
                self.assertFalse(self.autoescape(name))

    def test_other_templates_are_still_escaped(self):
        for name in ("example.html", "example.html.jinja", "example.jinja", None):
            with self.subTest(name=name):
                self.assertTrue(self.autoescape(name))
