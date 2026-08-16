import json
from unittest import mock

from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.core.vector_indexes import PageIndex, PageSource, render_first_paragraph


class TestRenderFirstParagraph(TestCase):
    def _page_with_body(self, blocks):
        return ContentPageFactory(body=json.dumps(blocks))

    def test_skips_alert_and_returns_first_text_block(self):
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


class TestPageSource(TestCase):
    def setUp(self):
        self.home = HomePageFactory()

    def _make_source(self):
        from apps.core.models.content import ContentPage

        return PageSource(queryset=ContentPage.objects.live().public())

    def test_get_content_includes_title_description_and_body(self):
        page = ContentPageFactory(
            parent=self.home,
            title="Managing snippets",
            search_description="A short summary.",
            body=json.dumps([{"type": "text", "value": "<p>Snippet content.</p>"}]),
        )
        content = self._make_source().get_content(page)

        self.assertIn("Managing snippets", content)
        self.assertIn("A short summary.", content)
        self.assertIn("Snippet content.", content)

    def test_get_content_strips_html_tags(self):
        page = ContentPageFactory(
            parent=self.home,
            body=json.dumps(
                [{"type": "text", "value": "<p>Text with <strong>bold</strong>.</p>"}]
            ),
        )
        content = self._make_source().get_content(page)

        self.assertNotIn("<p>", content)
        self.assertIn("Text with bold.", content)

    def test_get_metadata_includes_locale(self):
        page = ContentPageFactory(parent=self.home, title="Managing snippets")
        metadata = self._make_source().get_metadata(page)

        self.assertEqual(metadata["locale"], page.locale.language_code)


class TestPageIndex(TestCase):
    def test_search_sources_applies_locale_filter(self):
        with mock.patch(
            "apps.core.vector_indexes.get_llm_service"
        ) as mock_get_llm_service:
            mock_get_llm_service.return_value = mock.Mock()
            index = PageIndex()

        fake_queryset = mock.Mock()
        fake_queryset.filter.return_value = "filtered"

        with mock.patch(
            "django_ai_core.contrib.index.base.VectorIndex.search_sources",
            return_value=fake_queryset,
        ):
            result = index.search_sources("query", locale="en")

        fake_queryset.filter.assert_called_once_with(locale="en")
        self.assertEqual(result, "filtered")
