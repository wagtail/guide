import json

from django.test import TestCase
from django.urls import reverse

from apps.core.factories import ContentPageFactory


def annotated_body(content="<p>Annotated content</p>", **kw):
    return json.dumps([{"type": "text_annotated", "value": {"content": content, **kw}}])


class TestAnnotatedTextBlockMarkdown(TestCase):
    """Annotations are plain text in Markdown, mirroring the HTML badge."""

    def _markdown(self, body):
        page = ContentPageFactory(body=body)
        return page.to_markdown(request=None, frontmatter=True)

    def test_change_type_and_version(self):
        markdown = self._markdown(annotated_body(version="7.4", change_type="added"))
        self.assertIn("Added in Wagtail 7.4: Annotated content\n", markdown)

    def test_change_type_only(self):
        markdown = self._markdown(annotated_body(change_type="changed"))
        self.assertIn("Changed: Annotated content\n", markdown)
        self.assertNotIn("in Wagtail", markdown)

    def test_version_only(self):
        # The HTML badge shows "Wagtail 6.3" on its own, so Markdown must too.
        markdown = self._markdown(annotated_body(version="6.3"))
        self.assertIn("Wagtail 6.3: Annotated content\n", markdown)

    def test_no_annotation(self):
        markdown = self._markdown(annotated_body())
        self.assertIn("Annotated content\n", markdown)
        self.assertNotIn("Wagtail", markdown)

    def test_llms_full_txt_includes_annotations(self):
        # llms-full.txt renders pages without a request, so the current site
        # must come from the page rather than from `wagtail_site()`.
        ContentPageFactory(
            body=annotated_body(version="7.4", change_type="added"),
        )
        response = self.client.get(reverse("llms_full_txt"))
        self.assertContains(response, "Added in Wagtail 7.4: Annotated content")
