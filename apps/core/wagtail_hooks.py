import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail_ai.panels import AIDescriptionFieldPanel

from apps.core.models.feedback import Feedback


class FeedbackViewSet(SnippetViewSet):
    model = Feedback
    base_url_path = "feedbackadmin"
    icon = "pilcrow"
    list_display = ("feedback", "feedback_text", "page")
    list_filter = ("feedback", "page")
    search_fields = ("feedback_text", "page__title")
    copy_view_enabled = False


register_snippet(FeedbackViewSet)


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
            "box-shadow": "0 1px 1px rgba(0, 0, 0, .2), 0 2px 0 0 rgba(255, 255, 255, .7) inset",
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


# Enable AI prompts on built-in field.
Page.promote_panels[0].args[0][-1] = AIDescriptionFieldPanel("search_description")
