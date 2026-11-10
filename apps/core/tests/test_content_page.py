import json
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

    def test_create_table_of_contents_nests_h3_and_h4(self):
        self.content_page.body = json.dumps(
            [
                {
                    "type": "text",
                    "value": (
                        "<h2>One</h2><h3>One one</h3><h4>One one one</h4>"
                        "<h3>One two</h3><h2>Two</h2>"
                    ),
                }
            ]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#one">One</a>'
            '<ul><li><a href="#one-one">One one</a>'
            '<ul><li><a href="#one-one-one">One one one</a></li></ul></li>'
            '<li><a href="#one-two">One two</a></li></ul></li>'
            '<li><a href="#two">Two</a></li></ul>',
        )

    def test_create_table_of_contents_skipped_heading_level(self):
        # A heading can only nest one level deeper than the previous one, so
        # content skipping levels (h2 to h4) still gets a well-formed list.
        self.content_page.body = json.dumps(
            [{"type": "text", "value": "<h2>One</h2><h4>Deep</h4><h2>Two</h2>"}]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#one">One</a>'
            '<ul><li><a href="#deep">Deep</a></li></ul></li>'
            '<li><a href="#two">Two</a></li></ul>',
        )

    def test_create_table_of_contents_without_h2(self):
        # The first heading is the top level, whatever it is.
        self.content_page.body = json.dumps(
            [{"type": "text", "value": "<h3>One</h3><h3>Two</h3>"}]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#one">One</a></li><li><a href="#two">Two</a></li></ul>',
        )

    def test_create_table_of_contents_heading_back_to_skipped_level(self):
        # h2 → h4 → h3: the h3 is a sibling of the h4 (both children of the
        # h2), and a following h4 nests under the h3.
        self.content_page.body = json.dumps(
            [
                {
                    "type": "text",
                    "value": "<h2>One</h2><h4>Two</h4><h3>Three</h3><h4>Four</h4>",
                }
            ]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#one">One</a>'
            '<ul><li><a href="#two">Two</a></li>'
            '<li><a href="#three">Three</a>'
            '<ul><li><a href="#four">Four</a></li></ul></li></ul></li></ul>',
        )

    def test_create_table_of_contents_shallower_heading_mid_page(self):
        # h3 → h2 → h3: the h2 becomes a top-level item, and the following
        # h3 nests under it rather than staying flat.
        self.content_page.body = json.dumps(
            [{"type": "text", "value": "<h3>One</h3><h2>Two</h2><h3>Three</h3>"}]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#one">One</a></li>'
            '<li><a href="#two">Two</a>'
            '<ul><li><a href="#three">Three</a></li></ul></li></ul>',
        )

    def test_escapes_heading_text(self):
        self.content_page.body = json.dumps(
            [
                {
                    "type": "text",
                    "value": "<h2>&lt;script&gt;alert(1)&lt;/script&gt;</h2>",
                }
            ]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#scriptalert1script">&lt;script&gt;alert(1)&lt;/script&gt;</a></li></ul>',
        )

    def test_escapes_existing_id(self):
        self.content_page.body = json.dumps(
            [
                {
                    "type": "text",
                    "value": '<h2 id="section&quot; onclick=&quot;alert(1)">Title</h2>',
                }
            ]
        )

        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#section&quot; onclick=&quot;alert(1)">Title</a></li></ul>',
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
