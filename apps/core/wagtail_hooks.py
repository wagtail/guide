import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)


@hooks.register("register_rich_text_features")
def register_inline_code_feature(features):
    feature_name = "inlineCode"
    type_ = "INLINECODE"
    tag = "span"

    control = {
        "type": type_,
        "label": "<>",
        "description": "Inline Code",
        "style": {
            "fontFamily": 'ui-monospace, Menlo, Monaco, "Cascadia Mono", "Segoe UI Mono", "Roboto Mono", "Oxygen Mono", "Ubuntu Monospace", "Source Code Pro", "Fira Mono", "Droid Sans Mono", "Courier New", monospace, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',  # noqa
        },
    }

    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {
            "style_map": {type_: {"element": tag, "props": {"class": "inline-code"}}}
        },
    }

    features.register_converter_rule("contentstate", feature_name, db_conversion)

    features.default_features.append("inlineCode")
