from django.utils.translation import gettext as _
from wagtail.core import blocks


class SectionStructValue(blocks.StructValue):
    def icon(self):
        return f"svg/{self.get('section')}.svg"


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

    class Meta:
        template = "home/section_block.html"
        value_class = SectionStructValue


class SectionGridBlock(blocks.ListBlock):
    def __init__(self, *args, **kwargs):
        kwargs.update({"child_block": SectionBlock(label=_("Section"))})
        super().__init__(*args, **kwargs)

    class Meta:
        label = _("Section grid")
        icon = "list-ul"
        template = "home/section_grid_block.html"
