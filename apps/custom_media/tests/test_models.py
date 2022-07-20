from unittest import TestCase

from wagtail.documents import get_document_model, get_document_model_string
from wagtail.documents.models import AbstractDocument
from wagtail.images import get_image_model, get_image_model_string
from wagtail.images.models import AbstractImage

from apps.custom_media.models import CustomDocument, CustomImage, CustomRendition


class TestCustomMedia(TestCase):
    def test_custom_image(self):
        # CustomImage is a subclass of AbstractImage
        self.assertIsInstance(CustomImage(), AbstractImage)

        # Image model can be used in the whole app
        # via `get_image_model_string` or `get_image_model`.
        self.assertEqual(get_image_model_string(), "custom_media.CustomImage")
        self.assertIsInstance(get_image_model()(), CustomImage)

    def test_custom_rendition(self):
        self.assertEqual(
            CustomRendition()._meta.unique_together,
            (("image", "filter_spec", "focal_point_key"),),
        )
        self.assertTrue(hasattr(CustomRendition, "image"))

    def test_custom_document(self):
        # CustomDocument is a subclass of AbstractDocument
        self.assertIsInstance(CustomDocument(), AbstractDocument)

        # CustomDocument model can be used in the whole app
        # via `get_document_model_string` or `get_document_model`.
        self.assertEqual(get_document_model_string(), "custom_media.CustomDocument")
        self.assertIsInstance(get_document_model()(), CustomDocument)
