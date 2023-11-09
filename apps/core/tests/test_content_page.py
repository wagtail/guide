from django.test import TestCase

from apps.core.factories import ContentPageFactory


class TestContentPage(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_create_table_of_contents_no_id(self):
        # If there's no id, generate it by slugifying the text.
        self.assertEqual(self.content_page.table_of_contents, "")
        self.content_page.body = '[{"type": "text", "value": "<h2>Foo bar</h2>"}]'
        self.content_page.save_revision()
        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#foo-bar">Foo bar</a></li></ul>',
        )

    def test_create_table_of_contents_existing_id(self):
        # Our custom AnchorBlockConverter for Draft.js isn't called when
        # translating with wagtail-localize, so the id isn't updated.
        # If there's an existing id, make sure to use that instead so the link
        # still works.
        self.assertEqual(self.content_page.table_of_contents, "")
        self.content_page.body = (
            '[{"type": "text", "value": "<h2 id=\\"something\\">ekkie</h2>"}]'
        )
        self.content_page.save_revision()
        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#something">ekkie</a></li></ul>',
        )
