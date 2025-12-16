from django.test import TestCase
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy

from apps.llms_txt.templatetags.llms_txt_tags import richtext_markdown


class TestRichtextMarkdownTag(TestCase):
    def test_call_with_text(self):
        result = richtext_markdown("Hello world!")
        self.assertEqual(result, "Hello world!\n\n")
        self.assertIsInstance(result, SafeString)

    def test_call_with_lazy(self):
        result = richtext_markdown(gettext_lazy("test"))
        self.assertEqual(result, "test\n\n")

    def test_call_with_none(self):
        result = richtext_markdown(None)
        self.assertEqual(result, "")
