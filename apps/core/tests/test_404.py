from http import HTTPStatus

from django.test import TestCase

from apps.core.factories import HomePageFactory

# Unprefixed, so the request is first redirected to the `/en/` URL.
MISSING_PATH = "/some-path-that-does-not-exist"


class TestPageNotFound(TestCase):
    def setUp(self):
        HomePageFactory()

    def test_html_by_default(self):
        response = self.client.get(MISSING_PATH, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
        self.assertIn("Accept", response["Vary"])

    def test_markdown_when_requested(self):
        response = self.client.get(
            MISSING_PATH, headers={"Accept": "text/markdown"}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response["Content-Type"], "text/markdown;charset=utf-8")
        self.assertIn("Accept", response["Vary"])
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("[llms.txt](/llms.txt)", response.content.decode())
