from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import RichTextBlock

VERSION_VALIDATOR = RegexValidator(
    regex=r"^\d+\.\d+$",
    message=_("Enter a version in x.y format, e.g. 7.4 or 8.10."),
)


class TextBlock(RichTextBlock):
    class Meta:
        template = "core/blocks/text.html"


class AnnotatedTextBlock(blocks.StructBlock):
    content = RichTextBlock()
    version = blocks.CharBlock(
        max_length=20,
        required=False,
        validators=[VERSION_VALIDATOR],
        help_text=_("Wagtail version, in x.y format, e.g. 7.4 or 8.10."),
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
        template = "core/blocks/text_annotated.html"
        icon = "pilcrow"
        label = _("Text (annotated)")
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
    ("text_annotated", AnnotatedTextBlock()),
    ("alert", AlertBlock()),
]
HOME_BLOCKS = [("section_grid", SectionGridBlock())]
