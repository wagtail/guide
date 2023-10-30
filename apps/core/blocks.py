from django.utils.translation import gettext as _
from wagtail import blocks
from wagtail.blocks import RichTextBlock


class TextBlock(RichTextBlock):
    class Meta:
        template = "core/blocks/text.html"


class SectionStructValue(blocks.StructValue):
    def icon(self):
        return f"core/svg/{self.get('section')}.svg"


class SectionBlock(blocks.StructBlock):
    section = blocks.ChoiceBlock(
        choices=[
            ("tutorial", _("Tutorial")),
            ("how-to", _("How-to")),
            ("reference", _("Reference")),
            ("explanation", _("Explanation")),
        ],
        label=_("Section"),
    )
    title = blocks.CharBlock(label=_("Title"))
    text = blocks.TextBlock(label=_("Text"))
    page = blocks.PageChooserBlock(label=_("Page"))

    class Meta:
        template = "core/blocks/section.html"
        value_class = SectionStructValue


class SectionGridBlock(blocks.ListBlock):
    def __init__(self, *args, **kwargs):
        kwargs.update({"child_block": SectionBlock(label=_("Section"))})
        super().__init__(*args, **kwargs)

    class Meta:
        label = _("Section grid")
        icon = "list-ul"
        template = "core/blocks/section_grid.html"


class AlertStructValue(blocks.StructValue):
    def icon(self):
        return f"core/svg/{self.get('alert_type').lower()}.svg"


class AlertBlock(blocks.StructBlock):
    alert_type = blocks.ChoiceBlock(
        choices=[
            ("Warning", _("Warning")),
            ("Note", _("Note")),
        ]
    )
    alert_body = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        template = "core/blocks/alert.html"
        value_class = AlertStructValue


CONTENT_BLOCKS = [("text", TextBlock()), ("alert", AlertBlock())]
HOME_BLOCKS = [("section_grid", SectionGridBlock())]
