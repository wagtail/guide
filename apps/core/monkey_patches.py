"""
Monkey patch `CopyPageForTranslationAction._copy_for_translation`.

The language code contains dots and needs to be converted into a valid slug.

One line is changed: `# Convert language_code into a valid slug`
"""

import logging

from django.db import transaction
from wagtail.actions.copy_for_translation import (
    CopyPageForTranslationAction,
    ParentNotTranslatedError,
)
from wagtail.coreutils import find_available_slug

logger = logging.getLogger(__name__)


# flake8: noqa: C901
@transaction.atomic
def _copy_for_translation(self, page, locale, copy_parents, alias, exclude_fields):
    # Find the translated version of the parent page to create the new page under
    parent = page.get_parent().specific
    slug = page.slug

    if not parent.is_root():
        try:
            translated_parent = parent.get_translation(locale)
        except parent.__class__.DoesNotExist:
            if not copy_parents:
                raise ParentNotTranslatedError("Parent page is not translated.")

            translated_parent = parent.copy_for_translation(
                locale, copy_parents=True, alias=True
            )
    else:
        # Don't duplicate the root page for translation. Create new locale as a sibling
        translated_parent = parent

        # Append language code to slug as the new page
        # will be created in the same section as the existing one
        # Convert language_code into a valid slug
        slug += "-" + locale.language_code.replace(".", "-")

    # Find available slug for new page
    slug = find_available_slug(translated_parent, slug)

    if alias:
        return page.create_alias(
            parent=translated_parent,
            update_slug=slug,
            update_locale=locale,
            reset_translation_key=False,
        )

    else:
        # Update locale on translatable child objects as well
        def process_child_object(
            original_page, page_copy, child_relation, child_object
        ):
            from wagtail.models import TranslatableMixin

            if isinstance(child_object, TranslatableMixin):
                child_object.locale = locale

        return page.copy(
            to=translated_parent,
            update_attrs={
                "locale": locale,
                "slug": slug,
            },
            copy_revisions=False,
            keep_live=False,
            reset_translation_key=False,
            process_child_object=process_child_object,
            exclude_fields=exclude_fields,
            log_action="wagtail.copy_for_translation",
        )


def patch_copy_for_translation_action():
    logger.warning(
        "Monkey patching `CopyPageForTranslationAction._copy_for_translation`"
    )

    CopyPageForTranslationAction._copy_for_translation = _copy_for_translation
