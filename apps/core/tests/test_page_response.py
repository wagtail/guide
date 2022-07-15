from django.test import TestCase
from wagtail.models import Page
from wagtail.models.sites import Site

from apps.core.models import ContentPage, HomePage


class TestPageResponseStatusCode(TestCase):
    def setUp(self):
        site = Site.objects.first()
        root = Page.get_first_root_node()
        homePage = HomePage(
            title="Test Home Page",
            slug="test-home-page",
        )
        root.add_child(instance=homePage)
        old_home = site.root_page
        site.root_page = homePage
        site.save()
        old_home.delete()
        homePage.slug = "home"
        homePage.save()
        self.homePage = homePage

        contentPage = ContentPage(
            title="Content Page",
            slug="content-page",
            body=[
                {"type": "text", "value": "some test content"},
                {"type": "text", "value": "some more test content"},
            ],
        )

        self.homePage.add_child(instance=contentPage)
        self.contentPage = contentPage

        self.contentPageRes = self.client.get(self.contentPage.url)
        self.homePageRes = self.client.get(self.homePage.url)

    def test_homepage_response_status_code(self):
        self.assertEqual(self.homePageRes.status_code, 200)

    def test_contentpage_response_status_code(self):
        self.assertEqual(self.contentPageRes.status_code, 200)

    def test_contentpage_content(self):
        self.assertContains(self.contentPageRes, text="some test content", count=1)
        self.assertContains(self.contentPageRes, text="some more test content", count=1)

    def test_contentpage_template_used(self):
        self.assertTemplateUsed(self.contentPageRes, template_name="base.html", count=1)
        self.assertTemplateUsed(
            self.contentPageRes, template_name="core/content_page.html", count=1
        )
        self.assertTemplateUsed(
            self.contentPageRes, template_name="core/blocks/text.html", count=2
        )
