from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.models import Page

from apps.home.blocks import SectionGridBlock


class HomePage(Page):
    subpage_types = ["content.ContentPage"]
    max_count = 1

    sections = StreamField(
        [("section_grid", SectionGridBlock())],
        use_json_field=True,
        null=True,
        min_num=1,
        max_num=1,
    )

    content_panels = Page.content_panels + [FieldPanel("sections")]
