from django.test import TestCase


class TestAPIV3(TestCase):
    def test_openapi_schema_is_available(self):
        res = self.client.get("/api/v3-preview/openapi.json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["content-type"], "application/json")

    def test_docs_page_is_available(self):
        res = self.client.get("/api/v3-preview/docs/")
        self.assertEqual(res.status_code, 200)

    def test_pages_list_is_available_anonymously(self):
        res = self.client.get("/api/v3-preview/pages/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("items", res.json())
