from http import HTTPStatus

from django.test import TestCase

from apps.core.factories import HomePageFactory

# path -> expected redirect target.
REDIRECTS = {
    # Old versioned URLs.
    "/en-6.0.x/how-to-guides/manage-snippets/": (
        "/en/how-to-guides/manage-snippets/?target_version=6.0.x"
    ),
    "/en-latest/": "/en/?target_version=latest",
    "/pt-br-6.0.x/x/": "/pt-br/x/?target_version=6.0.x",
    # Existing query strings are preserved, alongside the target version.
    "/en-6.0.x/foo/?q=1": "/en/foo/?q=1&target_version=6.0.x",
    # Developer-docs-style `latest` URLs, where `/latest` is removed.
    "/en/latest/": "/en/",
    "/en/latest": "/en/",
    "/en/latest/how-to-guides/manage-redirects/": (
        "/en/how-to-guides/manage-redirects/"
    ),
    "/pt-br/latest/x/": "/pt-br/x/",
    "/en/latest/foo/?q=1": "/en/foo/?q=1",
}


class TestVersionedUrlRedirectMiddleware(TestCase):
    def setUp(self):
        self.home = HomePageFactory()

    def test_redirects(self):
        for path, expected in REDIRECTS.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertEqual(response["Location"], expected)

    def test_non_versioned_url_passes_through(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_bogus_version_shape_passes_through(self):
        response = self.client.get("/en-99/x/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_latest_longer_path_segment_passes_through(self):
        response = self.client.get("/en/latesting/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_to_versioned_url_passes_through(self):
        response = self.client.post("/en-6.0.x/edit/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_to_latest_url_passes_through(self):
        response = self.client.post("/en/latest/edit/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
