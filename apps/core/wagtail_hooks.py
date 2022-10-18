import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from apps.core.models.feedback import Feedback


class FeedbackAdmin(ModelAdmin):
    model = Feedback
    base_url_path = "feedbackadmin"
    menu_icon = "pilcrow"
    list_display = ("feedback", "feedback_text", "page")
    list_filter = ("feedback", "page")
    search_fields = ("feedback_text", "page__title")


modeladmin_register(FeedbackAdmin)


@hooks.register("register_rich_text_features")
def register_inline_code_feature(features):
    features.default_features.append("code")


@hooks.register("register_rich_text_features")
def register_keyboard_input_text_style(features):
    feature_name = "keyboard_input"
    type_ = "KEYBOARDINPUT"
    tag = "kbd"

    control = {
        "type": type_,
        "label": "⌘",
        "description": "Keyboard input style",
        "style": {
            "background-color": "#eee",
            "border-radius": "3px",
            "border": "1px solid #b4b4b4",
            "box-shadow": "0 1px 1px rgba(0, 0, 0, .2), 0 2px 0 0 rgba(255, 255, 255, .7) inset",  # noqa
            "color": "#333",
            "display": "inline-block",
            "font-size": ".85em",
            "font-weight": "700",
            "line-height": "1",
            "padding": "2px 4px",
            "white-space": "nowrap",
        },
    }

    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: tag}},
    }

    features.register_converter_rule("contentstate", feature_name, db_conversion)

    features.default_features.append("keyboard_input")
