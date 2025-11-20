from django.test import TestCase

from apps.core.factories import HomePageFactory


class TestHomePage(TestCase):
    def setUp(self):
        self.homepage = HomePageFactory()
        self.homepage.introduction = ('<p><i>Want to learn more about Wagtail’s '
                                      'future?</i></p>')
        self.homepage.save()

    def test_render_homepage_with_introduction(self):
        response = self.client.get(self.homepage.url)

        self.assertContains(response, ('<p><i>Want to learn more about Wagtail’s '
                                      'future?</i></p>'))
