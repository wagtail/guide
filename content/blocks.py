from wagtail.core.blocks import RichTextBlock

class ContentBlock(RichTextBlock):
    class Meta:
        template = 'content/content_block.html'