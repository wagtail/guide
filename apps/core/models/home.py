from django.conf import settings
from django.db import models
from django.http.response import Http404
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from ..blocks import HOME_BLOCKS
from ..views import Custom404


class HomePage(Page):
    subpage_types = ["core.SectionPage", "core.ContentPage"]
    max_count = 1
    introduction = models.TextField(blank=True)

    sections = StreamField(
        HOME_BLOCKS,
        use_json_field=True,
        null=True,
        min_num=1,
        max_num=1,
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("sections"),
    ]

    def route(self, request, path_components):
        try:
            return super().route(request, path_components)
        except Http404:
            raise Custom404(
                fallback_pages=self.get_fallback_pages(request, path_components)
            )

    def get_fallback_pages(self, request, path_components):
        # No fallback for main locale.
        if (language_code := self.locale.language_code) == settings.LANGUAGE_CODE:
            return []

        # Work out translations of the page requested corresponding to:
        # 1. Same version but in english (if language requested isn't english)
        # 2. Same language using latest version (if version requested isn't the latest)
        # 3. Latest version in English
        language, version = language_code.rsplit("-", maxsplit=1)
        codes = {language, "en"}
        versions = {version, "latest"}
        possible_language_codes = [
            f"{code}-{version}" for code in codes for version in versions
        ]
        translations = self.get_translations(inclusive=False).filter(
            locale__language_code__in=possible_language_codes
        )

        fallback_pages = []
        for page in translations:
            try:
                result = Page.route(page, request, path_components)
            except Http404:
                continue
            else:
                fallback_pages.append(result.page)

        return fallback_pages
