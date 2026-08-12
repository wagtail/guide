from unittest.mock import patch

from django.test import TestCase

from apps.core.factories import ContentPageFactory


class TestContentPage(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_create_table_of_contents_no_headings(self):
        self.assertEqual(self.content_page.table_of_contents, "")

    def test_create_table_of_contents_no_id(self):
        # If there's no id, generate it by slugifying the text.
        self.content_page.body = '[{"type": "text", "value": "<h2>Foo bar</h2>"}]'

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#foo-bar">Foo bar</a></li></ul>',
        )

    def test_create_table_of_contents_existing_id(self):
        # Our custom AnchorBlockConverter for Draft.js isn't called when
        # translating with wagtail-localize, so the id isn't updated.
        # If there's an existing id, make sure to use that instead so the link
        # still works.
        self.content_page.body = (
            '[{"type": "text", "value": "<h2 id=\\"something\\">ekkie</h2>"}]'
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#something">ekkie</a></li></ul>',
        )

    def test_table_of_contents_is_cached_on_page_instance(self):
        with patch(
            "apps.core.models.content.create_table_of_contents",
            return_value="generated table of contents",
        ) as create_table_of_contents:
            first_result = self.content_page.table_of_contents
            second_result = self.content_page.table_of_contents

        self.assertEqual(first_result, "generated table of contents")
        self.assertEqual(second_result, "generated table of contents")
        create_table_of_contents.assert_called_once_with(self.content_page.body)

    def test_historical_revision_ignores_stored_table_of_contents(self):
        revision = self.content_page.save_revision()
        revision.content["table_of_contents"] = "stored table of contents"

        revision_page = revision.as_object()

        self.assertEqual(revision_page.table_of_contents, "")
