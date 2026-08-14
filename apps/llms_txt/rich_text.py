from django.utils.functional import Promise
from django.utils.safestring import mark_safe
from draftjs_exporter import MARKDOWN_CONFIG, HTMLExporter
from wagtail.admin.rich_text.converters.contentstate import ContentstateConverter
from wagtail.rich_text import RichText
from wagtail.rich_text import features as feature_registry


class MarkdownContentstateConverter(ContentstateConverter):
    def __init__(self):
        features = feature_registry.get_default_features()
        super().__init__(features)
        self.exporter = HTMLExporter(MARKDOWN_CONFIG)

    def to_markdown_format(self, html):
        json_str = self.from_database_format(html)
        return self.to_database_format(json_str)


def richtext_markdown(value: RichText | Promise | str | None):
    if isinstance(value, Promise):
        value = str(value)
    elif isinstance(value, RichText):
        value = value.source
    elif value is None:
        return ""

    html = MarkdownContentstateConverter().to_markdown_format(value)
    return mark_safe(html)
