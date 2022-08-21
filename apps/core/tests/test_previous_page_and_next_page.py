from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory
from apps.core.templatetags.core_tags import next_page, previous_page


class TestNavigationButtons(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.first_child = ContentPageFactory(parent=self.home)
        self.subchild1 = ContentPageFactory(parent=self.first_child)
        self.subchild2 = ContentPageFactory(parent=self.first_child)
        self.last_child = ContentPageFactory(parent=self.home)

    def test_previous_page_filter(self):

        # A page’s first child links to its parent as previous page.
        self.assertEqual(previous_page(self.first_child).specific, self.home)
        # A page’s first child links to its parent as previous page.
        self.assertEqual(previous_page(self.subchild1).specific, self.first_child)
        # If there is a previous sibling, we link to it.
        self.assertEqual(previous_page(self.subchild2).specific, self.subchild1)
        # If the previous sibling page has child pages,
        # we link to the sibling’s last child.
        self.assertEqual(previous_page(self.last_child).specific, self.subchild2)

    def test_next_page_filter(self):
        # A parent page links to its first child as next page.
        self.assertEqual(next_page(self.home).specific, self.first_child)
        # A parent page links to its first child as next page.
        self.assertEqual(next_page(self.first_child).specific, self.subchild1)
        # If there is next sibling, we link to it.
        self.assertEqual(next_page(self.subchild1).specific, self.subchild2)
        # If there is no next sibling and child, we link to the first
        # next sibling of the parent page.
        self.assertEqual(next_page(self.subchild2).specific, self.last_child)
        # If the page does not have any next siblings, children and
        # next sibling of the parent page, we return None.
        self.assertEqual(next_page(self.last_child), None)
