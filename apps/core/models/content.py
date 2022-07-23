from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.models import Page

from ..blocks import CONTENT_BLOCKS


class ContentPage(Page):
    show_in_menus_default = True
    subpage_types = ["core.ContentPage"]

    body = StreamField(
        CONTENT_BLOCKS,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [FieldPanel("body")]
