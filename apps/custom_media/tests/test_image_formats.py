from django.test import SimpleTestCase
from wagtail.images.formats import get_image_format


class TestImageFormats(SimpleTestCase):
    def test_fullwidth_filter_spec(self):
        fullwidth = get_image_format("fullwidth")
        self.assertEqual(fullwidth.filter_spec, "width-900")
