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

    def get_context(self, request, *args, **kwargs):
        if self.live and self.show_in_menus:
            context = super().get_context(request, *args, **kwargs)
            pages = Page.objects.live().in_menu()
            context.update(
                previous=pages.filter(path__lt=self.path).last(),
                next=pages.filter(path__gt=self.path).first()
            )
            return context
