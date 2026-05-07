from django.test import TestCase

from apps.core.factories import ContentPageFactory
from apps.core.models.content import create_table_of_contents


class TestContentPage(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_can_create_page(self):
        self.assertIsNotNone(self.content_page)
        self.assertIsNotNone(self.content_page.id)

    def test_table_of_contents_property_exists(self):
        toc = self.content_page.table_of_contents
        self.assertIsInstance(toc, str)


class TableOfContentsTest(TestCase):
    def test_create_table_of_contents_empty(self):
        toc = create_table_of_contents("")
        self.assertEqual(toc, "")

    def test_create_table_of_contents_no_id(self):
        # If there's no id, generate it by slugifying the text.
        body_html = "<h2>Foo bar</h2>"
        toc = create_table_of_contents(body_html)
        self.assertEqual(
            toc,
            '<ul><li><a href="#foo-bar">Foo bar</a></li></ul>',
        )

    def test_create_table_of_contents_existing_id(self):
        # Our custom AnchorBlockConverter for Draft.js isn't called when
        # translating with wagtail-localize, so the id isn't updated.
        # If there's an existing id, make sure to use that instead so the link
        # still works.
        body_html = '<h2 id="something">ekkie</h2>'
        toc = create_table_of_contents(body_html)
        self.assertEqual(
            toc,
            '<ul><li><a href="#something">ekkie</a></li></ul>',
        )

    def test_create_table_of_contents_simple(self):
        body_html = """
            <h2>Introduction</h2>
            <p>Some text</p>
            <h3>Details</h3>
            <p>More text</p>
            <h2>Conclusion</h2>
        """
        toc = create_table_of_contents(body_html)

        self.assertIn('<li><a href="#introduction">Introduction</a>', toc)
        self.assertIn('<ul><li><a href="#details">Details</a></li></ul>', toc)
        self.assertIn('<li><a href="#conclusion">Conclusion</a>', toc)

    def test_create_table_of_contents_nested(self):
        body_html = """
            <h2>First</h2>
            <h3>Nested 1</h3>
            <h3>Nested 2</h3>
            <h2>Second</h2>
        """
        toc = create_table_of_contents(body_html)

        expected_part = '<li><a href="#first">First</a><ul><li><a href="#nested-1">Nested 1</a></li><li><a href="#nested-2">Nested 2</a></li></ul></li>'
        self.assertIn(expected_part, toc)

    def test_create_table_of_contents_orphaned_h3(self):
        body_html = """
            <h3>Orphaned</h3>
            <h2>Main</h2>
        """
        toc = create_table_of_contents(body_html)

        self.assertIn('<li><a href="#orphaned">Orphaned</a></li>', toc)
        self.assertIn('<li><a href="#main">Main</a>', toc)
