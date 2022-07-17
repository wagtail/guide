from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.models import Page

from ..blocks import HOME_BLOCKS


class HomePage(Page):
    subpage_types = ["core.ContentPage"]
    max_count = 1

    sections = StreamField(
        HOME_BLOCKS,
        use_json_field=True,
        null=True,
        min_num=1,
        max_num=1,
    )

    content_panels = Page.content_panels + [FieldPanel("sections")]
