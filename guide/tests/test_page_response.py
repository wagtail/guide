from django.test import TestCase
from wagtail.models import Page
from content.models import ContentPage
from home.models import HomePage

class TestPageResponseStatusCode(TestCase):
    fixtures = ["test.json"]
    # def setUp(self):
    #     self.parent = Page.objects.get(url_path='/home/')
    #     homePage = HomePage(
    #         title = 'Test Home Page',
    #         slug = 'test-home-page',
    #     )
    #     contentPage = ContentPage(
    #         title = 'Test Content Page',
    #         slug = 'test-content-page',
    #         body = [
    #             {
    #                 "type": "content",
    #                 "value": "test content test content"
    #             }
    #         ]
    #     )
    #     self.parent.add_child(instance=homePage)
    #     HomePage.objects.first().add_child(instance=contentPage)

    def test_homepage_response_status_code(self):
        homepage = HomePage.objects.first()
        res = self.client.get(homepage.url)
        self.assertEqual(res.status_code, 200)

    def test_contentpage_response_status_code(self):
        contentpage = ContentPage.objects.first()
        res = self.client.get(contentpage.url)
        self.assertEqual(res.status_code, 200)