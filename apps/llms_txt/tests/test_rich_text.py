from django.test import TestCase
from wagtail_factories import DocumentFactory

from apps.core.factories import ContentPageFactory, LocaleFactory
from apps.llms_txt.rich_text import richtext_markdown


class TestRichtextMarkdown(TestCase):
    def test_to_markdown_paragraph(self):
        html = "<p><b>Bold text</b></p>"
        markdown = richtext_markdown(html)
        self.assertEqual(markdown, "**Bold text**\n\n")

    def test_to_markdown_headings(self):
        html = "<h1>Heading 1</h1><h2>Heading 2</h2>"
        markdown = richtext_markdown(html)
        self.assertEqual(markdown, "Heading 1\n\n## Heading 2\n\n")

    def test_to_markdown_internal_links(self):
        en_locale = LocaleFactory(language_code="en")
        page = ContentPageFactory(locale=en_locale)
        html = f'<p><a linktype="page" id="{page.id}">Example</a></p>'
        markdown = richtext_markdown(html)
        self.assertEqual(markdown, f"[Example](/en/{page.slug}/)\n\n")

    def test_to_markdown_broken_internal_links(self):
        # Broken page links – e.g. when the target page has been deleted – are
        # retained by Wagtail with a None URL, and should render as plain text.
        html = '<p><a linktype="page" id="999999">Broken link</a></p>'
        markdown = richtext_markdown(html)
        self.assertEqual(markdown, "Broken link\n\n")

    def test_to_markdown_document_links(self):
        document = DocumentFactory(title="Setup guide")
        html = f'<p><a linktype="document" id="{document.id}">Setup guide</a></p>'
        markdown = richtext_markdown(html)
        self.assertEqual(markdown, f"[Setup guide]({document.url})\n\n")

    def test_to_markdown_broken_document_links(self):
        html = '<p><a linktype="document" id="999999">Gone doc</a></p>'
        markdown = richtext_markdown(html)
        self.assertEqual(markdown, "Gone doc\n\n")
