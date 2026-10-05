import json

from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.blocks import StructValue
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.rich_text import RichText
from wagtail.search import index
from wagtail_ai.panels import AITitleFieldPanel

from apps.core.models.feedback import Feedback
from apps.llms_txt.mixins import MarkdownRouteMixin

from ..blocks import CONTENT_BLOCKS


def get_rich_text_sources(body):
    for block in body:
        if isinstance(block.value, StructValue):
            values = block.value.values()
        else:
            values = [block.value]
        for value in values:
            if isinstance(value, RichText):
                yield value.source


def create_table_of_contents(body):
    # Headings and their ids are stored in the rich text HTML, so read them
    # from there rather than rendering the body a second time, which would
    # repeat the database lookups for every link in it.
    soup = BeautifulSoup("".join(get_rich_text_sources(body)), "lxml")
    headings = soup.select("h2,h3")
    toc = ""
    if headings:
        toc += "<ul>"
        for heading in headings:
            anchor = heading.attrs.get("id", slugify(heading.text))
            toc += format_html('<li><a href="#{}">{}</a></li>', anchor, heading.text)
        toc += "</ul>"
    return toc


class ContentPage(MarkdownRouteMixin, Page):
    show_in_menus_default = True
    subpage_types = ["core.ContentPage"]

    body = StreamField(CONTENT_BLOCKS)

    @cached_property
    def table_of_contents(self):
        return create_table_of_contents(self.body)

    content_panels = [
        AITitleFieldPanel("title"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [index.SearchField("body")]

    api_fields = [
        APIField("body", writable=True),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        if self.live and self.show_in_menus:
            pages = Page.objects.live().public().in_menu()
            context.update(
                previous=pages.filter(path__lt=self.path).last(),
                next=pages.filter(path__gt=self.path).first(),
            )

        return context

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            data = json.loads(request.body)
            if "pk" in data:
                feedback = Feedback.objects.get(pk=data["pk"])
                feedback.feedback_text = data["feedback_text"]
                feedback.save()
                data = {"pk": feedback.pk}
            else:
                new_feedback = Feedback(
                    feedback=data["feedback"],
                    page=self,
                )
                new_feedback.save()
                data = {"pk": new_feedback.pk}

            return HttpResponse(json.dumps(data))
        else:
            return super().serve(request, *args, **kwargs)
