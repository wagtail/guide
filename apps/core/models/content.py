import json

from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.template import Context, Template
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail_ai.panels import AITitleFieldPanel

from apps.core.models.feedback import Feedback
from apps.llms_txt.mixins import MarkdownRouteMixin

from ..blocks import CONTENT_BLOCKS


def create_table_of_contents(body):
    template = Template("{% load wagtailcore_tags %}{% include_block body %}")
    content = template.render(Context({"body": body}))
    soup = BeautifulSoup(content, "html.parser")
    headings = soup.select("h2,h3,h4")
    if not headings:
        return ""

    # Nest h3 within h2, and h4 within h3. The first heading is always the
    # top level, and a heading can only be one level deeper than the previous
    # one, so content skipping levels (e.g. h2 to h4) nests a single level
    # rather than leaving an empty list item.
    toc = "<ul>"
    open_items = []  # Heading levels of the <li> elements still open, deepest last.
    for heading in headings:
        level = int(heading.name[1])
        if open_items:
            if level > open_items[-1]:
                # Deeper heading: nest a new list within the previous item.
                open_items.append(level)
                toc += "<ul>"
            else:
                # Same or shallower heading: close the lists of the deeper
                # items, up to the closest ancestor shallower than this one.
                while len(open_items) > 1 and level <= open_items[-2]:
                    open_items.pop()
                    toc += "</li></ul>"
                toc += "</li>"
        else:
            open_items.append(level)
        anchor = heading.attrs.get("id", slugify(heading.text))
        toc += format_html('<li><a href="#{}">{}</a>', anchor, heading.text)
    toc += "</li>"
    for _ in open_items[1:]:
        toc += "</ul></li>"
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
