from http import HTTPStatus

from django.test import TestCase

from apps.core.factories import HomePageFactory


class TestVersionedUrlRedirectMiddleware(TestCase):
    def setUp(self):
        self.home = HomePageFactory()

    def test_versioned_url_redirects(self):
        response = self.client.get("/en-6.0.x/how-to-guides/manage-snippets/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response["Location"],
            "/en/how-to-guides/manage-snippets/?target_version=6.0.x",
        )

    def test_redirect_preserves_existing_query_string(self):
        response = self.client.get("/en-6.0.x/foo/?q=1")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response["Location"],
            "/en/foo/?q=1&target_version=6.0.x",
        )

    def test_latest_version_redirects(self):
        response = self.client.get("/en-latest/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "/en/?target_version=latest")

    def test_region_language_version_redirects(self):
        response = self.client.get("/pt-br-6.0.x/x/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "/pt-br/x/?target_version=6.0.x")

    def test_non_versioned_url_passes_through(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_bogus_version_shape_passes_through(self):
        response = self.client.get("/en-99/x/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_to_versioned_url_passes_through(self):
        response = self.client.post("/en-6.0.x/edit/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
