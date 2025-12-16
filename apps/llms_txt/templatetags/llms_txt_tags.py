from django import template
from django.utils.functional import Promise
from django.utils.safestring import mark_safe
from wagtail.rich_text import RichText

from apps.llms_txt.rich_text import MarkdownContentstateConverter

register = template.Library()


@register.filter
def richtext_markdown(value: RichText | Promise | str | None):
    if isinstance(value, Promise):
        value = str(value)
    elif isinstance(value, RichText):
        value = value.source
    elif value is None:
        return ""

    html = MarkdownContentstateConverter().to_markdown_format(value)
    return mark_safe(html)
