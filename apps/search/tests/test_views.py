from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from apps.core.factories import ContentPageFactory, HomePageFactory

SEARCH_JSON_URL = "/en/search_json/"


class TestSearchJson(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.section = ContentPageFactory(parent=self.home, title="Section")

    def search(self, query):
        response = self.client.get(SEARCH_JSON_URL, {"query": query})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def get_query_count(self, query):
        with CaptureQueriesContext(connection) as ctx:
            self.search(query)
        return len(ctx.captured_queries)

    def test_no_query(self):
        response = self.client.get(SEARCH_JSON_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_parent_section(self):
        page = ContentPageFactory(parent=self.section, title="Zebra page")
        ContentPageFactory(parent=page, title="Zebra subpage")
        ContentPageFactory(parent=self.home, title="Zebra section")

        results = self.search("zebra")

        self.assertEqual(
            sorted((result["title"], result["parent_section"]) for result in results),
            [
                ("Zebra page", "Section"),
                ("Zebra section", "Home"),
                ("Zebra subpage", "Section"),
            ],
        )

    def test_full_url(self):
        page = ContentPageFactory(parent=self.section, title="Zebra page")

        results = self.search("zebra")

        self.assertEqual([result["full_url"] for result in results], [page.full_url])

    def test_results_do_not_add_queries(self):
        ContentPageFactory(parent=self.section, title="Zebra 0")
        self.search("zebra")
        expected = self.get_query_count("zebra")

        other_section = ContentPageFactory(parent=self.home, title="Other")
        for i in range(1, 5):
            ContentPageFactory(parent=other_section, title=f"Zebra {i}")

        self.assertEqual(len(self.search("zebra")), 5)
        self.assertEqual(self.get_query_count("zebra"), expected)
