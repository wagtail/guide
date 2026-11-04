import json

from django.test import TestCase
from django.urls import reverse


class TestAPICatalog(TestCase):
    def get_linkset(self):
        response = self.client.get(reverse("api_catalog"))
        self.assertEqual(response.status_code, 200)
        return response, json.loads(response.content)

    def test_content_type_has_rfc9727_profile(self):
        response, _ = self.get_linkset()
        self.assertEqual(
            response["Content-Type"],
            'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"',
        )

    def test_anchor_is_the_v3_api(self):
        _, linkset = self.get_linkset()
        self.assertEqual(
            [entry["anchor"] for entry in linkset["linkset"]],
            ["http://testserver/api/v3-preview/pages/"],
        )

    def test_lists_public_v3_endpoints(self):
        _, linkset = self.get_linkset()
        items = {item["href"] for item in linkset["linkset"][0]["item"]}
        self.assertEqual(items, {"http://testserver/api/v3-preview/pages/"})

    def test_describes_the_api(self):
        _, linkset = self.get_linkset()
        entry = linkset["linkset"][0]
        self.assertEqual(
            entry["service-desc"][0]["href"],
            "http://testserver/api/v3-preview/openapi.json",
        )
        self.assertEqual(
            entry["service-doc"][0]["href"],
            "http://testserver/api/v3-preview/docs/",
        )

    def test_does_not_advertise_authenticated_endpoints(self):
        response, _ = self.get_linkset()
        body = response.content.decode()
        for path in ("/sites/", "/schema/", "/whoami/", "/actions/"):
            with self.subTest(path=path):
                self.assertNotIn(path, body)
