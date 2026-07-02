from django.utils.translation import gettext as _
from wagtail import blocks
from wagtail.blocks import RichTextBlock

WAGTAIL_VERSIONS = [
    "4.1",
    "4.2",
    "5.0",
    "5.1",
    "5.2",
    "6.0",
    "6.1",
    "6.2",
    "6.3",
    "6.4",
    "7.0",
    "7.1",
    "7.2",
    "7.3",
    "7.4",
    "8.0",
]


class TextBlock(RichTextBlock):
    class Meta:
        template = "core/blocks/text.html"


class TextBlockVersioned(blocks.StructBlock):
    content = RichTextBlock(features=["bold", "italic", "link"])
    version = blocks.ChoiceBlock(
        choices=[(v, v) for v in WAGTAIL_VERSIONS],
        required=False,
    )
    change_type = blocks.ChoiceBlock(
        choices=[
            ("added", _("Added")),
            ("changed", _("Changed")),
            ("removed", _("Removed")),
        ],
        required=False,
    )

    class Meta:
        template = "core/blocks/text_versioned.html"
        icon = "pilcrow"
        label = _("Text (versioned)")
        form_layout = blocks.BlockGroup(
            children=["content"],
            settings=["version", "change_type"],
        )


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


CONTENT_BLOCKS = [
    ("text", TextBlock()),
    ("text_versioned", TextBlockVersioned()),
    ("alert", AlertBlock()),
]
HOME_BLOCKS = [("section_grid", SectionGridBlock())]
