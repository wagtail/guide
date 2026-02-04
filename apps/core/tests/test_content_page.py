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

    def test_create_table_of_contents_nested_h3(self):
        # Test that h3 headings are nested under h2 headings
        self.assertEqual(self.content_page.table_of_contents, "")
        self.content_page.body = (
            '[{"type": "text", "value": "<h2>Parent</h2><h3>Child 1</h3><h3>Child 2</h3>"}]'
        )
        self.content_page.save_revision()
        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#parent">Parent</a><ul>'
            '<li><a href="#child-1">Child 1</a></li>'
            '<li><a href="#child-2">Child 2</a></li>'
            '</ul></li></ul>',
        )

    def test_create_table_of_contents_multiple_h2_with_h3(self):
        # Test multiple h2 headings with their own h3 children
        self.assertEqual(self.content_page.table_of_contents, "")
        self.content_page.body = (
            '[{"type": "text", "value": "<h2>Section 1</h2><h3>Sub 1</h3><h2>Section 2</h2><h3>Sub 2</h3>"}]'
        )
        self.content_page.save_revision()
        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#section-1">Section 1</a><ul>'
            '<li><a href="#sub-1">Sub 1</a></li>'
            '</ul></li>'
            '<li><a href="#section-2">Section 2</a><ul>'
            '<li><a href="#sub-2">Sub 2</a></li>'
            '</ul></li></ul>',
        )

    def test_create_table_of_contents_h2_without_h3(self):
        # Test h2 headings without any h3 children
        self.assertEqual(self.content_page.table_of_contents, "")
        self.content_page.body = (
            '[{"type": "text", "value": "<h2>Section 1</h2><h2>Section 2</h2>"}]'
        )
        self.content_page.save_revision()
        self.assertEqual(
            self.content_page.table_of_contents,
            '<ul><li><a href="#section-1">Section 1</a></li>'
            '<li><a href="#section-2">Section 2</a></li></ul>',
        )
