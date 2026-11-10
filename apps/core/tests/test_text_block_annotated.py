import json

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.core.blocks import AnnotatedTextBlock
from apps.core.factories import ContentPageFactory


class TestAnnotatedTextBlock(TestCase):
    def _page_with_annotated_block(self, content, version=None, change_type=None):
        value = {"content": content}
        if version is not None:
            value["version"] = version
        if change_type is not None:
            value["change_type"] = change_type
        body = json.dumps([{"type": "text_annotated", "value": value}])
        return ContentPageFactory(body=body)

    def test_renders_badge_with_change_type_and_version(self):
        page = self._page_with_annotated_block(
            "<p>Added content</p>", version="7.0", change_type="added"
        )
        response = self.client.get(page.url)
        self.assertContains(response, "Added in Wagtail 7.0", count=1)
        self.assertContains(response, "version-badge version-badge--added", count=1)
        self.assertContains(response, "<p>Added content</p>", count=1)

    def test_renders_badge_with_multidigit_version(self):
        page = self._page_with_annotated_block(
            "<p>Added content</p>", version="8.10", change_type="added"
        )
        response = self.client.get(page.url)
        self.assertContains(response, "Added in Wagtail 8.10", count=1)

    def test_renders_badge_with_change_type_only(self):
        page = self._page_with_annotated_block(
            "<p>Some text</p>", change_type="changed"
        )
        response = self.client.get(page.url)
        self.assertContains(response, "version-badge version-badge--changed", count=1)
        self.assertNotContains(response, "in Wagtail")

    def test_renders_badge_with_version_only(self):
        page = self._page_with_annotated_block(
            "<p>Annotated content</p>", version="6.3"
        )
        response = self.client.get(page.url)
        self.assertContains(response, "Wagtail 6.3", count=1)
        self.assertContains(response, "version-badge", count=1)

    def test_no_badge_without_version_or_change_type(self):
        page = self._page_with_annotated_block("<p>Plain content</p>")
        response = self.client.get(page.url)
        self.assertNotContains(response, "version-badge")
        self.assertContains(response, "<p>Plain content</p>", count=1)

    def test_removed_change_type_uses_base_badge_class(self):
        page = self._page_with_annotated_block(
            "<p>Some text</p>", change_type="removed"
        )
        response = self.client.get(page.url)
        self.assertContains(response, "version-badge version-badge--removed", count=1)

    def test_uses_annotated_template(self):
        page = self._page_with_annotated_block("<p>Content</p>", change_type="added")
        response = self.client.get(page.url)
        self.assertTemplateUsed(response, "core/blocks/text_annotated.html", count=1)

    def test_version_validation_accepts_x_y_format(self):
        version_block = AnnotatedTextBlock().child_blocks["version"]
        for valid in ["7.4", "8.10", "10.0", "0.1"]:
            version_block.clean(valid)

    def test_version_validation_rejects_other_formats(self):
        version_block = AnnotatedTextBlock().child_blocks["version"]
        for invalid in ["7", "7.4.1", "v7.4", "seven-four", "7.x"]:
            with self.assertRaises(ValidationError):
                version_block.clean(invalid)

    def test_version_validation_optional_allows_empty(self):
        version_block = AnnotatedTextBlock().child_blocks["version"]
        version_block.clean("")
