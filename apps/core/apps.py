from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from .monkey_patches import patch_copy_for_translation_action

        patch_copy_for_translation_action()
