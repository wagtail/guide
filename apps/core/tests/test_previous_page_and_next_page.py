from django.test import TestCase

from apps.core.factories import ContentPageFactory, HomePageFactory


class TestNavigationButtons(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.first_child = ContentPageFactory(parent=self.home)
        self.subchild1 = ContentPageFactory(parent=self.first_child)
        self.subchild2 = ContentPageFactory(parent=self.first_child)
        self.last_child = ContentPageFactory(parent=self.home)
        self.res_first_child = self.client.get(self.first_child.url)
        self.res_subchild1 = self.client.get(self.subchild1.url)
        self.res_subchild2 = self.client.get(self.subchild2.url)
        self.res_last_child = self.client.get(self.last_child.url)

    def test_previous_page(self):
        self.assertIsNone(self.res_first_child.context["previous"])
        self.assertEqual(
            self.res_subchild1.context["previous"].specific, self.first_child
        )
        self.assertEqual(
            self.res_subchild2.context["previous"].specific, self.subchild1
        )
        self.assertEqual(
            self.res_last_child.context["previous"].specific, self.subchild2
        )

    def test_next_page(self):
        self.assertEqual(self.res_first_child.context["next"].specific, self.subchild1)
        self.assertIsNone(self.res_last_child.context["next"])
        self.assertEqual(self.res_subchild1.context["next"].specific, self.subchild2)
        self.assertEqual(self.res_subchild2.context["next"].specific, self.last_child)
