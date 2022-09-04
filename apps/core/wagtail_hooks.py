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
