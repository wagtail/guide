import json

from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from wagtail.models import Site

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.llms_txt.views import (
    LLMS_FULL_TXT_TEMPLATE,
    LLMS_TXT_TEMPLATE,
    SKILL_DESCRIPTION,
    get_cache_key,
)


class TestLLMsTxtViews(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.content_page = ContentPageFactory(parent=self.home_page)
        self.site = Site.objects.get(is_default_site=True)

    def cache_key(self, template_name):
        return get_cache_key(self.site.pk, template_name)

    def test_llms_txt_renders_pages(self):
        response = self.client.get("/llms.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn(self.content_page.title.encode(), response.content)

    def test_llms_txt_includes_usage_guidance(self):
        response = self.client.get(reverse("llms_txt"))
        self.assertContains(response, "**When to use this guide:**")
        self.assertContains(response, "**When not to use this guide:**")
        self.assertContains(response, "**How to use this guide:**")
        self.assertContains(response, "https://docs.wagtail.org/")

    def test_llms_txt_links_to_optional_resources(self):
        response = self.client.get(reverse("llms_txt"))
        root_url = self.site.root_url
        for name in ("llms_full_txt", "agent_skill", "agent_skills_index"):
            with self.subTest(name=name):
                self.assertContains(response, f"]({root_url}{reverse(name)})")

    def test_llms_txt_h2_sections_are_link_lists(self):
        # The llms.txt spec reserves H2 sections for link lists.
        ContentPageFactory(
            parent=self.home_page, search_description="First line.\r\nSecond line."
        )
        cache.clear()
        response = self.client.get(reverse("llms_txt"))
        lines = response.content.decode().splitlines()
        headings = [line for line in lines if line.startswith("## ")]
        self.assertEqual(headings, ["## Table of Contents", "## Optional"])
        start = lines.index(headings[0])
        for line in lines[start:]:
            if line and not line.startswith("## "):
                with self.subTest(line=line):
                    self.assertTrue(line.startswith("- ["))

    def test_agent_skills_index_description(self):
        response = self.client.get(reverse("agent_skills_index"))
        skill = response.json()["skills"][0]
        self.assertEqual(skill["description"], SKILL_DESCRIPTION)

    def test_llms_full_txt_renders_pages(self):
        response = self.client.get("/llms-full.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn(self.content_page.title.encode(), response.content)

    def test_llms_full_txt_does_not_fetch_body_per_page(self):
        names = ("Second", "Third", "Fourth")
        for name in names:
            ContentPageFactory(
                parent=self.home_page,
                title=f"{name} page",
                body=json.dumps(
                    [{"type": "text", "value": f"<p>{name} page body content.</p>"}]
                ),
            )
        cache.clear()

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get("/llms-full.txt")

        self.assertEqual(response.status_code, 200)
        body_queries = [
            query
            for query in ctx.captured_queries
            if 'FROM "core_contentpage"' in query["sql"] and '"body"' in query["sql"]
        ]
        self.assertEqual(len(body_queries), 1)
        for name in names:
            self.assertIn(f"{name} page body content.".encode(), response.content)

    def test_responses_are_cached(self):
        for path, template_name in (
            ("/llms.txt", LLMS_TXT_TEMPLATE),
            ("/llms-full.txt", LLMS_FULL_TXT_TEMPLATE),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIsNotNone(cache.get(self.cache_key(template_name)))

    def test_cached_response_is_reused(self):
        self.client.get("/llms-full.txt")
        cache.set(self.cache_key(LLMS_FULL_TXT_TEMPLATE), "cached content", 60)

        response = self.client.get("/llms-full.txt")

        self.assertIn(b"cached content", response.content)

    def test_publish_invalidates_cache(self):
        self.client.get("/llms-full.txt")
        self.content_page.save_revision().publish()

        self.assertIsNone(cache.get(self.cache_key(LLMS_FULL_TXT_TEMPLATE)))
        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))

    def test_unpublish_invalidates_cache(self):
        self.client.get("/llms.txt")
        self.content_page.unpublish()

        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))

    def test_delete_invalidates_cache(self):
        self.client.get("/llms.txt")
        self.content_page.delete()

        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))

    def test_move_invalidates_cache(self):
        second_page = ContentPageFactory(parent=self.home_page, title="Second page")
        self.client.get("/llms.txt")
        self.content_page.move(second_page, pos="right")

        self.assertIsNone(cache.get(self.cache_key(LLMS_TXT_TEMPLATE)))
