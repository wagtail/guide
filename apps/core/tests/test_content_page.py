from django.test import TestCase

from apps.core.factories import ContentPageFactory


class TestContentPage(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_create_table_of_contents(self):
        assert self.content_page.table_of_contents == ""
        self.content_page.body = '[{"type": "text", "value": "<h2>ekkie</h2>"}]'
        self.content_page.save_revision()
        assert (
            self.content_page.table_of_contents
            == '<ul><li><a href="#ekkie">ekkie</a></li></ul>'
        )
