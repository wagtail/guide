from django.test import TestCase

from apps.core.factories import ContentPageFactory, LocaleFactory
from apps.llms_txt.rich_text import MarkdownContentstateConverter


class TestMarkdownContentstateConverter(TestCase):
    def setUp(self):
        self.converter = MarkdownContentstateConverter()

    def test_to_markdown_format_paragraph(self):
        html = "<p><b>Bold text</b></p>"
        markdown = self.converter.to_markdown_format(html)
        self.assertEqual(markdown, "**Bold text**\n\n")

    def test_to_markdown_format_headings(self):
        html = "<h1>Heading 1</h1><h2>Heading 2</h2>"
        markdown = self.converter.to_markdown_format(html)
        self.assertEqual(markdown, "Heading 1\n\n## Heading 2\n\n")

    def test_to_markdown_format_internal_links(self):
        en_latest = LocaleFactory(language_code="en-latest")
        page = ContentPageFactory(locale=en_latest)
        html = f'<p><a linktype="page" id="{page.id}">Example</a></p>'
        markdown = self.converter.to_markdown_format(html)
        self.assertEqual(markdown, f"[Example](/en-latest/{page.slug}/)\n\n")
