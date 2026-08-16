import json
from unittest import mock

from django.test import TestCase

from apps.core.agents import LocalizedSuggestedContentAgent
from apps.core.factories import ContentPageFactory, HomePageFactory


class FakeQuerySet(list):
    """A list that supports .filter() (for locale) like a queryish queryset."""

    def filter(self, **kwargs):
        return self


class FakeIndex:
    """Minimal stand-in for PageIndex, with a scripted search_sources."""

    def __init__(self, pages):
        self._pages = pages

    def search_sources(self, query, *, locale=None, **kwargs):
        return FakeQuerySet(self._pages)


class TestLocalizedSuggestedContentAgent(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.agent = LocalizedSuggestedContentAgent()

    def _make_page(self, **kwargs):
        kwargs.setdefault("parent", self.home)
        return ContentPageFactory(**kwargs)

    def _run(self, current_page, pages, **kwargs):
        """Run the agent with a fake index returning the given pages."""
        fake_index = FakeIndex(pages)
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            return self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(current_page.pk)],
                content="ignored preview text",
                **kwargs,
            )

    def _run_and_capture_query(self, page):
        """Run the agent with a recording index that captures the search query."""
        captured = []

        class RecordingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                captured.append(query)
                return FakeQuerySet([])

        with mock.patch(
            "apps.core.agents.index_registry.get",
            return_value=lambda: RecordingIndex([]),
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )
        return captured[0]

    def test_builds_query_from_title_description_and_body_snippet(self):
        page = self._make_page(
            title="Manage snippets",
            search_description="Reusable content elements.",
            body=json.dumps(
                [{"type": "text", "value": "<p>Snippets let you reuse content.</p>"}]
            ),
        )
        query = self._run_and_capture_query(page)

        self.assertIn("Manage snippets", query)
        self.assertIn("Reusable content elements.", query)
        self.assertIn("Snippets let you reuse content.", query)

    def test_falls_back_to_content_when_current_page_not_found(self):
        captured = []

        class RecordingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                captured.append(query)
                return FakeQuerySet([])

        with mock.patch(
            "apps.core.agents.index_registry.get",
            return_value=lambda: RecordingIndex([]),
        ):
            result = self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=["999999"],
                content="Fallback preview content",
                chunk_size=100,
            )

        self.assertEqual(captured[0], "Fallback preview content")
        self.assertEqual(result, [])

    def test_excludes_pages_in_exclude_pks(self):
        page = self._make_page(title="Source page")
        already_related = self._make_page(title="Already added")

        fake_index = FakeIndex([already_related])
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            result = self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk), str(already_related.pk)],
                content="ignored",
            )

        self.assertEqual(result, [])

    def test_respects_limit(self):
        page = self._make_page(title="Source page")
        related = [self._make_page(title=f"Match {i}") for i in range(5)]

        result = self._run(page, related, limit=2)

        self.assertEqual(len(result), 2)

    def test_preserves_order(self):
        page = self._make_page(title="Source page")
        first = self._make_page(title="First match")
        second = self._make_page(title="Second match")

        result = self._run(page, [first, second])

        self.assertEqual([r["title"] for r in result], ["First match", "Second match"])

    def test_derives_locale_from_current_page_and_filters_by_it(self):
        page = self._make_page(title="Source page")
        filter_calls = []

        class SpyingQuerySet(FakeQuerySet):
            def filter(self, **kwargs):
                filter_calls.append(kwargs)
                return self

        class SpyingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                qs = SpyingQuerySet(self._pages)
                if locale:
                    qs = qs.filter(locale=locale)
                return qs

        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: SpyingIndex([])
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )

        self.assertEqual(filter_calls, [{"locale": page.locale.language_code}])
