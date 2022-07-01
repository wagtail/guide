from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from content.blocks import ContentBlock
class ContentPage(Page):
    subpage_types = ['content.ContentPage']
    body = StreamField([
        ('content', ContentBlock())
    ], block_counts={
        'content': {
            'min_num': 1,
        }
    }, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]
