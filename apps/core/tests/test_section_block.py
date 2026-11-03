from django.test import TestCase
from django.utils import translation

from apps.core.blocks import SectionBlock


class TestSectionBlockIcon(TestCase):
    @staticmethod
    def get_icon(section, language_code):
        value = SectionBlock().to_python(
            {
                "section": section,
                "title": "Tutorial",
                "text": "Learn the basics.",
                "page": None,
            }
        )
        with translation.override(language_code):
            return value.icon()

    def test_ltr_uses_default_icon(self):
        self.assertEqual(self.get_icon("tutorial", "en"), "core/svg/tutorial.svg")

    def test_rtl_uses_rtl_icon_when_available(self):
        self.assertEqual(self.get_icon("tutorial", "ar"), "core/svg/rtl/tutorial.svg")

    def test_rtl_falls_back_to_default_icon(self):
        # Only some sections have a hand-tuned RTL icon.
        self.assertEqual(self.get_icon("reference", "ar"), "core/svg/reference.svg")
