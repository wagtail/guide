from unittest import TestCase

from wagtail.documents import get_document_model
from wagtail.images import get_image_model

from apps.custom_media.factories import DocumentFactory, ImageFactory


class TestFactory(TestCase):
    def test_image_factory(self):
        self.assertIsInstance(ImageFactory(), get_image_model())

    def test_document_factory(self):
        self.assertIsInstance(DocumentFactory(), get_document_model())
