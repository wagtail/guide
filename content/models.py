from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.core import blocks

class ContentPage(Page):
    subpage_types = ['content.ContentPage']
    body = StreamField([
        ('content', blocks.RichTextBlock(required=True, help_text='Rich-text block'))
    ], block_counts={
        'content': {
            'min_num': 1,
        }
    }, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]
