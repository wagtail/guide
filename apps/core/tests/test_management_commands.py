from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page


class TestBuildFixtures(TestCase):
    def test_build_fixtures(self):
        self.assertEqual(Page.objects.all().count(), 2)
        call_command("buildfixtures")
        self.assertGreater(Page.objects.all().count(), 20)
        for page in Page.objects.all().exclude(pk=Page.get_first_root_node().pk):
            self.assertEqual(self.client.get(page.url).status_code, HTTPStatus.OK)

    def test_build_fixtures_creates_admin_superuser(self):
        call_command("buildfixtures")
        user = get_user_model().objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password("changeme"))
