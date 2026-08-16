import json
from unittest import mock

from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.core.vector_indexes import PageIndex, PageSource, render_first_paragraph


class TestRenderFirstParagraph(TestCase):
    def _page_with_body(self, blocks):
        return ContentPageFactory(body=json.dumps(blocks))

    def test_returns_first_text_block(self):
        page = self._page_with_body(
            [{"type": "text", "value": "<p>First paragraph.</p>"}]
        )
        self.assertEqual(render_first_paragraph(page), "First paragraph.")

    def test_skips_alert_block_and_returns_first_text_block(self):
        page = self._page_with_body(
            [
                {
                    "type": "alert",
                    "value": {
                        "alert_type": "Note",
                        "alert_body": "<p>An alert callout.</p>",
                    },
                },
                {"type": "text", "value": "<p>The real content.</p>"},
            ]
        )
        self.assertEqual(render_first_paragraph(page), "The real content.")

    def test_returns_text_annotated_block_content(self):
        page = self._page_with_body(
            [
                {
                    "type": "text_annotated",
                    "value": {"content": "<p>Annotated paragraph.</p>"},
                }
            ]
        )
        self.assertEqual(render_first_paragraph(page), "Annotated paragraph.")

    def test_returns_empty_string_when_no_text_blocks(self):
        page = self._page_with_body(
            [
                {
                    "type": "alert",
                    "value": {
                        "alert_type": "Note",
                        "alert_body": "<p>Only an alert here.</p>",
                    },
                }
            ]
        )
        self.assertEqual(render_first_paragraph(page), "")

    def test_returns_empty_string_for_empty_body(self):
        page = self._page_with_body([])
        self.assertEqual(render_first_paragraph(page), "")


class TestPageSource(TestCase):
    def setUp(self):
        self.home = HomePageFactory()

    def _make_source(self):
        # Avoid instantiating CoreEmbeddingTransformer (which requires a
        # configured LLM service) by building a PageSource directly.
        from apps.core.models.content import ContentPage

        return PageSource(queryset=ContentPage.objects.live().public())

    def test_get_content_includes_title_and_body_text(self):
        page = ContentPageFactory(
            parent=self.home,
            title="Managing snippets",
            body=json.dumps([{"type": "text", "value": "<p>Snippet content.</p>"}]),
        )
        source = self._make_source()
        content = source.get_content(page)

        self.assertIn("Managing snippets", content)
        self.assertIn("Snippet content.", content)

    def test_get_content_includes_search_description(self):
        page = ContentPageFactory(
            parent=self.home,
            title="Managing snippets",
            search_description="A short summary of the page.",
        )
        source = self._make_source()
        content = source.get_content(page)

        self.assertIn("A short summary of the page.", content)

    def test_get_content_includes_seo_title_when_different(self):
        page = ContentPageFactory(
            parent=self.home,
            title="Managing snippets",
            seo_title="Snippets - Full SEO Title",
        )
        source = self._make_source()
        content = source.get_content(page)

        self.assertIn("Snippets - Full SEO Title", content)

    def test_get_content_omits_seo_title_when_same_as_title(self):
        page = ContentPageFactory(parent=self.home, title="Managing snippets")
        page.seo_title = page.title
        source = self._make_source()
        content = source.get_content(page)

        # Title should only appear once (not duplicated as seo_title).
        self.assertEqual(content.count("Managing snippets"), 1)

    def test_get_content_strips_html_tags(self):
        page = ContentPageFactory(
            parent=self.home,
            body=json.dumps(
                [{"type": "text", "value": "<p>Text with <strong>bold</strong>.</p>"}]
            ),
        )
        source = self._make_source()
        content = source.get_content(page)

        self.assertNotIn("<p>", content)
        self.assertNotIn("<strong>", content)
        self.assertIn("Text with bold.", content)

    def test_uses_paragraph_chunk_transformer(self):
        from django_ai_core.contrib.index.chunking import ParagraphChunkTransformer

        source = self._make_source()
        self.assertIsInstance(source.chunk_transformer, ParagraphChunkTransformer)

    def test_get_metadata_includes_locale(self):
        page = ContentPageFactory(parent=self.home, title="Managing snippets")
        source = self._make_source()
        metadata = source.get_metadata(page)

        self.assertEqual(metadata["locale"], page.locale.language_code)


class TestPageIndex(TestCase):
    def test_search_sources_applies_locale_filter(self):
        with mock.patch(
            "apps.core.vector_indexes.get_llm_service"
        ) as mock_get_llm_service:
            mock_get_llm_service.return_value = mock.Mock()
            index = PageIndex()

        fake_queryset = mock.Mock()
        fake_queryset.filter.return_value = "filtered-queryset"

        with mock.patch(
            "django_ai_core.contrib.index.base.VectorIndex.search_sources",
            return_value=fake_queryset,
        ):
            result = index.search_sources("some query", locale="en")

        fake_queryset.filter.assert_called_once_with(locale="en")
        self.assertEqual(result, "filtered-queryset")

    def test_search_sources_skips_filter_when_no_locale(self):
        with mock.patch(
            "apps.core.vector_indexes.get_llm_service"
        ) as mock_get_llm_service:
            mock_get_llm_service.return_value = mock.Mock()
            index = PageIndex()

        fake_queryset = mock.Mock()

        with mock.patch(
            "django_ai_core.contrib.index.base.VectorIndex.search_sources",
            return_value=fake_queryset,
        ):
            result = index.search_sources("some query")

        fake_queryset.filter.assert_not_called()
        self.assertEqual(result, fake_queryset)
