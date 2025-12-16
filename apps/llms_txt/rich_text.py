from draftjs_exporter.html import HTML as HTMLExporter
from draftjs_exporter_markdown import BLOCK_MAP, ENGINE, ENTITY_DECORATORS, STYLE_MAP
from wagtail.admin.rich_text.converters.contentstate import (
    ContentstateConverter,
    block_fallback,
    entity_fallback,
    style_fallback,
)
from wagtail.rich_text import features as feature_registry


class MarkdownContentstateConverter(ContentstateConverter):
    def __init__(self):
        features = feature_registry.get_default_features()
        super().__init__(features)

        # See https://github.com/thibaudcolas/draftjs_exporter_markdown.
        exporter_config = {
            "block_map": {
                **BLOCK_MAP,
                "fallback": block_fallback,
            },
            "style_map": {
                **STYLE_MAP,
                "FALLBACK": style_fallback,
            },
            "entity_decorators": {
                **ENTITY_DECORATORS,
                "FALLBACK": entity_fallback,
            },
            "engine": ENGINE,
        }

        self.exporter = HTMLExporter(exporter_config)

    def to_markdown_format(self, html):
        json_str = self.from_database_format(html)
        return self.to_database_format(json_str)
