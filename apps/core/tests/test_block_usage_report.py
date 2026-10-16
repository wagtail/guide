import json
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.core.reports import iter_annotated_blocks


def _annotated_body(**kwargs):
    value = {"content": kwargs.pop("content", "<p>Some content</p>")}
    value.update(kwargs)
    return json.dumps([{"type": "text_annotated", "value": value}])


class TestBlockUsageReport(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.user = get_user_model().objects.create_superuser(
            username="admin", password="test"
        )
        self.client.login(username="admin", password="test")
        self.url = reverse("block_usage_report")

    def test_report_accessible_by_superuser(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_report_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_pages_without_annotated_blocks_excluded(self):
        ContentPageFactory(body=json.dumps([{"type": "text", "value": "<p>Hi</p>"}]))
        response = self.client.get(self.url)
        self.assertContains(response, "No pages with versioned blocks found.")

    def test_removed_block_at_outdated_version_flagged(self):
        ContentPageFactory(body=_annotated_body(change_type="removed", version="7.0"))
        response = self.client.get(self.url)
        self.assertContains(response, "Removed")
        self.assertContains(response, "7.0")
        self.assertContains(response, "Needs update")

    def test_removed_block_at_current_version_not_flagged(self):
        ContentPageFactory(body=_annotated_body(change_type="removed", version="7.4"))
        response = self.client.get(self.url)
        self.assertContains(response, "Removed")
        self.assertContains(response, "Up to date")

    def test_outdated_version_flagged(self):
        ContentPageFactory(body=_annotated_body(change_type="added", version="5.0"))
        response = self.client.get(self.url)
        self.assertContains(response, "5.0")
        self.assertNotContains(response, "Outdated")
        self.assertContains(response, "Needs update")

    def test_current_version_not_outdated(self):
        ContentPageFactory(body=_annotated_body(change_type="added", version="7.4"))
        response = self.client.get(self.url)
        self.assertNotContains(response, "Outdated")
        self.assertContains(response, "Up to date")

    def test_flagged_pages_sorted_first(self):
        ContentPageFactory(
            title="Flagged page",
            body=_annotated_body(change_type="added", version="5.0"),
        )
        ContentPageFactory(
            title="Clean page",
            body=json.dumps(
                [
                    {"type": "text_annotated", "value": {"content": "<p>ok</p>"}},
                ]
            ),
        )
        response = self.client.get(self.url)
        body = response.content.decode()
        self.assertTrue(body.index("Flagged page") < body.index("Clean page"))


class TestIterAnnotatedBlocks(TestCase):
    def setUp(self):
        self.home = HomePageFactory()

    def test_yields_only_annotated_blocks(self):
        body = json.dumps(
            [
                {"type": "text", "value": "<p>plain</p>"},
                {"type": "text_annotated", "value": {"content": "<p>a</p>"}},
                {"type": "text_annotated", "value": {"content": "<p>b</p>"}},
            ]
        )
        page = ContentPageFactory(body=body)
        blocks = list(iter_annotated_blocks(page))
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0][0], 1)
        self.assertEqual(blocks[1][0], 2)

    def test_empty_when_no_annotated_blocks(self):
        body = json.dumps([{"type": "text", "value": "<p>plain</p>"}])
        self.assertEqual(list(iter_annotated_blocks(ContentPageFactory(body=body))), [])
