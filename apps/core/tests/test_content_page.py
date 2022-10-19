from django.test import TestCase
from wagtail.admin.panels import get_form_for_model

from apps.core.factories import ContentPageFactory
from apps.core.models.content import ContentPage, ContentPageForm


class TestContentPage(TestCase):
    def setUp(self):
        self.content_page = ContentPageFactory()

    def test_create_table_of_contents(self):
        form_class = get_form_for_model(
            ContentPage,
            form_class=ContentPageForm,
            fields=["title", "slug", "body"],
        )
        form = form_class(
            data={
                "title": self.content_page.title,
                "slug": self.content_page.slug,
                "body-count": "1",
                "body-0-deleted": "",
                "body-0-type": "text",
                "body-0-order": "0",
                "body-0-value": """{"blocks":[{"key":"vxo1m","text":"ekkie","type":"header-two","depth":0,"inlineStyleRanges":[],"entityRanges":[],"data":{}}],"entityMap":{}}""",  # noqa
            },
            instance=self.content_page,
        )
        assert form.is_valid()
        assert (
            form.instance.table_of_contents
            == '<ul><li><a href="#ekkie">ekkie</a></li></ul>'  # noqa
        )
