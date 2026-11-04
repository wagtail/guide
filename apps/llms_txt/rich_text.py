from django.utils.functional import Promise
from django.utils.safestring import mark_safe
from wagtail.admin.rich_text.converters.markdown_db import MarkdownConverter
from wagtail.rich_text import RichText


def richtext_markdown(value: RichText | Promise | str | None):
    """Convert Wagtail's database rich text representation to Markdown.

    Uses Wagtail's own converter, which renders all of Wagtail's entity types
    (page and document links, images, embeds) and degrades dangling references
    – e.g. links to deleted pages – to plain text rather than crashing.
    """
    if isinstance(value, Promise):
        value = str(value)
    elif isinstance(value, RichText):
        value = value.source
    elif value is None:
        return ""

    return mark_safe(MarkdownConverter().from_database_format(value, resolved=True))
