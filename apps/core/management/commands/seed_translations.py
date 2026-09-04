from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from wagtail.models import Locale, Page
from wagtail_localize.machine_translators import get_machine_translator
from wagtail_localize.models import Translation, TranslationSource
from wagtail_localize.views.edit_translation import apply_machine_translation


class Command(BaseCommand):
    help = "Seed initial translations for target locales"

    def add_arguments(self, parser):
        parser.add_argument("--locale", type=str, help="Single target locale code")
        parser.add_argument(
            "--locales", type=str, help="Comma-separated target locale codes"
        )

        page_group = parser.add_mutually_exclusive_group()
        page_group.add_argument("--page", type=str)
        page_group.add_argument("--subtree", type=str)

    def _resolve_locale(self, code, valid_codes):
        """Returns (Locale | None, reason | None)."""
        if code == settings.LANGUAGE_CODE:
            return None, "source language"
        if code not in valid_codes:
            return None, "not in WAGTAIL_GUIDE_LANGUAGES"
        locale, _ = Locale.objects.get_or_create(language_code=code)
        return locale, None

    def _select_pages(self, options, source_locale):
        qs = Page.objects.filter(locale=source_locale, live=True).specific()
        if options["page"]:
            return qs.filter(slug__iexact=options["page"])
        if options["subtree"]:
            return qs.filter(slug__istartswith=options["subtree"])
        return qs.exclude(depth=1)

    def _get_or_create_bot_user(self, display_name):
        """Get or create a superuser for attributing machine translations."""
        slug = display_name.lower().replace(" ", "-")  # "DeepL" -> "deepl"
        username = f"{slug}-bot"
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"is_superuser": True, "is_staff": True, "email": ""},
        )
        return user

    def handle(self, *args, **options):
        raw = options["locales"] or options["locale"]
        if not raw:
            self.stderr.write(
                self.style.ERROR("Error: --locale or --locales is required")
            )
            return

        requested = [c.strip().lower() for c in raw.split(",") if c.strip()]

        valid_codes = dict(settings.WAGTAIL_GUIDE_LANGUAGES)
        target_locales = []
        for code in requested:
            locale, reason = self._resolve_locale(code, valid_codes)
            if locale is None:
                self.stdout.write(f"  {code}: skipped ({reason})")
                continue
            target_locales.append(locale)
            self.stdout.write(f"  {code}: ready")

        source_locale = Locale.objects.get(language_code=settings.LANGUAGE_CODE)
        pages = self._select_pages(options, source_locale)
        if not pages:
            self.stdout.write(self.style.WARNING("No source pages matched."))
            return

        created_translations = []

        for locale in target_locales:
            self.stdout.write(f"\nTranslating into {locale.language_code}:")
            for page in pages:
                source, _ = TranslationSource.get_or_create_from_instance(page)
                translation, created = Translation.objects.get_or_create(
                    source=source, target_locale=locale
                )
                created_translations.append(translation)
                if not created:
                    self.stdout.write(
                        f"  {page.slug}: skipped (already in translation)"
                    )
                    continue
                page.copy_for_translation(locale, copy_parents=True)
                self.stdout.write(f"  {page.slug}: copied -> draft")

        translator = get_machine_translator()
        if translator is None:
            self.stdout.write(self.style.WARNING("No machine translator configured"))
        else:
            bot_user = self._get_or_create_bot_user(translator.display_name)
            source_locale = Locale.objects.get(language_code=settings.LANGUAGE_CODE)
            supported = [
                t
                for t in created_translations
                if translator.can_translate(t.source.locale, t.target_locale)
            ]
            for t in supported:
                apply_machine_translation(t.id, bot_user, translator)
                self.stdout.write(
                    f"  translated {t.source.object_id} -> {t.target_locale.language_code}"
                )

        for translation in created_translations:
            translation.save_target(publish=False)
            self.stdout.write(
                f"  {translation.target_locale.language_code}: saved as draft"
            )
