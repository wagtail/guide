from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.models import Page

from ..blocks import CONTENT_BLOCKS


class ContentPage(Page):
    subpage_types = ["core.ContentPage"]

    body = StreamField(
        CONTENT_BLOCKS,
        block_counts={
            "content": {
                "min_num": 1,
            }
        },
        use_json_field=True,
    )

    content_panels = Page.content_panels + [FieldPanel("body")]
