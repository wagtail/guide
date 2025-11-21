from django.test import TestCase

from apps.core.factories import HomePageFactory


class TestHomePage(TestCase):
    def setUp(self):
        self.homepage = HomePageFactory()
        self.homepage.introduction = f'<p>Want to learn more about <a id="{self.homepage.id}" linktype="page">Wagtail’s future</a>?</p>'
        self.homepage.save()

    def test_render_homepage_with_introduction(self):
        response = self.client.get(self.homepage.url)

        self.assertContains(
            response,
            (
                '<p>Want to learn more about <a href="/en-latest/">Wagtail’s future</a>?</p>'
            ),
        )
