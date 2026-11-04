from django.test import TestCase


class TestAPIV2(TestCase):
    def test_pages_list_is_available(self):
        res = self.client.get("/api/v2/pages/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["content-type"], "application/json")

    def test_images_list_is_available(self):
        res = self.client.get("/api/v2/images/")
        self.assertEqual(res.status_code, 200)

    def test_documents_list_is_available(self):
        res = self.client.get("/api/v2/documents/")
        self.assertEqual(res.status_code, 200)
