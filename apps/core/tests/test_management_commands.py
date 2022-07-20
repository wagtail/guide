from http import HTTPStatus

from django.core.management import call_command
from django.test import TestCase
from wagtail.core.models import Page


class TestBuildFixtures(TestCase):
    def test_build_fixtures(self):
        self.assertEqual(Page.objects.all().count(), 2)
        call_command("buildfixtures")
        self.assertEqual(Page.objects.all().count(), 22)
        for page in Page.objects.all().exclude(pk=Page.get_first_root_node().pk):
            self.assertEqual(self.client.get(page.url).status_code, HTTPStatus.OK)
