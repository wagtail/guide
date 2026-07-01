from django.conf import settings
from django.http.response import Http404
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.llms_txt.mixins import MarkdownRouteMixin

from ..blocks import HOME_BLOCKS
from ..views import Custom404


class HomePage(MarkdownRouteMixin, Page):
    subpage_types = ["core.ContentPage"]
    max_count = 1
    introduction = RichTextField(blank=True)

    sections = StreamField(
        HOME_BLOCKS,
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
        if self.locale.language_code == settings.LANGUAGE_CODE:
            return []

        translations = self.get_translations(inclusive=False)

        fallback_pages = []
        for page in translations:
            try:
                result = Page.route(page, request, path_components)
            except Http404:
                continue
            else:
                fallback_pages.append(result.page)

        return fallback_pages
