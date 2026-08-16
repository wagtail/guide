import json

from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.template import Context, Template
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail_ai.panels import AIMultipleChooserPanel, AITitleFieldPanel

from apps.core.models.feedback import Feedback
from apps.llms_txt.mixins import MarkdownRouteMixin

from ..blocks import CONTENT_BLOCKS


def create_table_of_contents(body):
    template = Template("{% load wagtailcore_tags %}{% include_block body %}")
    content = template.render(Context({"body": body}))
    soup = BeautifulSoup(content, "lxml")
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
        AIMultipleChooserPanel(
            "related_pages",
            chooser_field_name="related_page",
            heading=_("Related pages"),
            label=_("Page"),
            max_num=5,
            vector_index="PageIndex",
            suggest_limit=2,
        ),
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

    @property
    def visible_related_pages(self):
        related_ids = list(self.related_pages.values_list("related_page_id", flat=True))
        if not related_ids:
            return []
        pages = Page.objects.live().public().filter(id__in=related_ids)
        pages_by_id = {p.pk: p for p in pages}
        return [pages_by_id[pid] for pid in related_ids if pid in pages_by_id]
