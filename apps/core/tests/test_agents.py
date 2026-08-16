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

    def _run_with_fake_index(self, current_page, pages, **kwargs):
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

    def test_builds_query_from_title_and_search_description(self):
        page = self._make_page(
            title="Manage snippets",
            search_description="Reusable content elements.",
        )
        captured_queries = []

        class RecordingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                captured_queries.append(query)
                return FakeQuerySet([])

        fake_index = RecordingIndex([])
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )

        self.assertEqual(len(captured_queries), 1)
        query = captured_queries[0]
        self.assertIn("Manage snippets", query)
        self.assertIn("Reusable content elements.", query)

    def test_includes_body_snippet_in_query(self):
        page = self._make_page(
            title="Manage snippets",
            body=json.dumps(
                [{"type": "text", "value": "<p>Snippets let you reuse content.</p>"}]
            ),
        )
        captured_queries = []

        class RecordingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                captured_queries.append(query)
                return FakeQuerySet([])

        fake_index = RecordingIndex([])
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )

        self.assertIn("Snippets let you reuse content.", captured_queries[0])

    def test_body_snippet_is_truncated_to_max_length(self):
        long_text = "A" * 1000
        page = self._make_page(
            title="Long page",
            body=json.dumps([{"type": "text", "value": f"<p>{long_text}</p>"}]),
        )
        captured_queries = []

        class RecordingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                captured_queries.append(query)
                return FakeQuerySet([])

        fake_index = RecordingIndex([])
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )

        query = captured_queries[0]
        snippet_in_query = query.split("Long page. ")[-1]
        self.assertLessEqual(
            len(snippet_in_query), self.agent.BODY_SNIPPET_LENGTH + len(". ")
        )

    def test_falls_back_to_content_when_current_page_not_found(self):
        captured_queries = []

        class RecordingIndex(FakeIndex):
            def search_sources(self, query, *, locale=None, **kwargs):
                captured_queries.append(query)
                return FakeQuerySet([])

        fake_index = RecordingIndex([])
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            result = self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=["999999"],
                content="Fallback preview content",
                chunk_size=100,
            )

        self.assertEqual(captured_queries[0], "Fallback preview content")
        self.assertEqual(result, [])

    def test_returns_empty_list_when_no_query_and_no_content(self):
        result = self.agent.execute(
            vector_index="PageIndex",
            exclude_pks=["999999"],
            content="",
        )
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
        related_pages = [self._make_page(title=f"Match {i}") for i in range(5)]

        result = self._run_with_fake_index(page, related_pages, limit=2)

        self.assertEqual(len(result), 2)

    def test_preserves_order(self):
        page = self._make_page(title="Source page")
        first = self._make_page(title="First match")
        second = self._make_page(title="Second match")

        result = self._run_with_fake_index(page, [first, second])

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

        fake_index = SpyingIndex([])
        with mock.patch(
            "apps.core.agents.index_registry.get", return_value=lambda: fake_index
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )

        self.assertEqual(filter_calls, [{"locale": page.locale.language_code}])

    def test_does_not_filter_by_locale_when_current_page_has_none(self):
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

        fake_index = SpyingIndex([])
        fake_page = mock.Mock(pk=page.pk, locale=None, specific=mock.Mock())
        fake_page.specific.title = "Source page"
        fake_page.specific.search_description = ""
        del fake_page.specific.body

        with (
            mock.patch(
                "apps.core.agents.index_registry.get", return_value=lambda: fake_index
            ),
            mock.patch("apps.core.agents.Page.objects.get", return_value=fake_page),
        ):
            self.agent.execute(
                vector_index="PageIndex",
                exclude_pks=[str(page.pk)],
                content="ignored",
            )

        self.assertEqual(filter_calls, [])

    def test_returns_edit_url_for_each_suggestion(self):
        page = self._make_page(title="Source page")
        related = self._make_page(title="Related page")

        result = self._run_with_fake_index(page, [related])

        self.assertEqual(len(result), 1)
        self.assertIn("editUrl", result[0])
        self.assertTrue(result[0]["editUrl"])
