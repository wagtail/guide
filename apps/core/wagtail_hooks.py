from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from apps.core.models.feedback import Feedback


class FeedbackAdmin(ModelAdmin):
    model = Feedback
    base_url_path = "feedbackadmin"
    menu_label = "Feedback"
    menu_icon = "pilcrow"
    add_to_settings_menu = False
    exclude_from_explorer = False
    add_to_admin_menu = True
    list_display = ("feedback", "feedback_text", "page")
    list_filter = ("feedback", "page")
    search_fields = ("feedback_text", "page")


modeladmin_register(FeedbackAdmin)
