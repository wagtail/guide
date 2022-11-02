from django.template import Context, Template
from django.test import TestCase
from django.utils import translation

from apps.core.factories import LocaleFactory
from apps.core.models.snippets import FooterContent


class TestFooter(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.en_latest = LocaleFactory(language_code="en-latest")
        cls.id_latest = LocaleFactory(language_code="id-latest")

        cls.footer_en = FooterContent.objects.first()
        cls.footer_id = cls.footer_en.copy_for_translation(cls.id_latest)

        cls.footer_id.copyright_text = (
            "Hak cipta dan hak terkait dibebaskan melalui CC0"
        )
        cls.footer_id.save()

        footer_item = cls.footer_id.footer_items.first()
        footer_item.title = "Tentang panduan ini"
        footer_item.description = (
            "Pelajari mengapa kami menyusun dokumen kami seperti ini"
        )
        footer_item.save()

    def test_footer_inclusion_tag_default(self):
        template = Template("{% load core_tags %}{% footer %}")
        result = template.render(Context({}))

        # Should contain original content
        self.assertIn("Copyright and related rights waived via", result)
        self.assertIn("About this guide", result)
        self.assertIn("Learn why we structured our documents like this", result)

        # Should not contain translated content
        self.assertNotIn("Hak cipta dan hak terkait dibebaskan melalui CC0", result)
        self.assertNotIn("Tentang panduan ini", result)
        self.assertNotIn(
            "Pelajari mengapa kami menyusun dokumen kami seperti ini", result
        )

    def test_footer_inclusion_tag_translated(self):
        # A normal request will go through LocaleMiddleware to activate the locale.
        translation.activate(self.id_latest.language_code)
        template = Template("{% load core_tags %}{% footer %}")
        result = template.render(Context({}))

        # Should contain translated content
        self.assertIn("Hak cipta dan hak terkait dibebaskan melalui CC0", result)
        self.assertIn("Tentang panduan ini", result)
        self.assertIn("Pelajari mengapa kami menyusun dokumen kami seperti ini", result)

        # Should not contain original content
        self.assertNotIn("Copyright and related rights waived via", result)
        self.assertNotIn("About this guide", result)
        self.assertNotIn("Learn why we structured our documents like this", result)

    def test_footer_inclusion_tag_untranslated(self):
        # A normal request will go through LocaleMiddleware to activate the locale.
        translation.activate("nl-latest")
        template = Template("{% load core_tags %}{% footer %}")
        result = template.render(Context({}))

        # Should contain original content
        self.assertIn("Copyright and related rights waived via", result)
        self.assertIn("About this guide", result)
        self.assertIn("Learn why we structured our documents like this", result)

        # Should not contain translated content from other locales
        self.assertNotIn("Hak cipta dan hak terkait dibebaskan melalui CC0", result)
        self.assertNotIn("Tentang panduan ini", result)
        self.assertNotIn(
            "Pelajari mengapa kami menyusun dokumen kami seperti ini", result
        )
