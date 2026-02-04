import json

from bs4 import BeautifulSoup
from django.db import models
from django.http import HttpResponse
from django.template import Context, Template
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel
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
    soup = BeautifulSoup(content, "lxml")
    headings = soup.select("h2,h3")
    toc = ""
    if headings:
        toc += "<ul>"
        nested_ul_open = False
        for i, heading in enumerate(headings):
            anchor = heading.attrs.get("id", slugify(heading.text))
            if heading.name == "h2":
                # Close any open nested list before starting a new h2
                if nested_ul_open:
                    toc += "</ul></li>"
                    nested_ul_open = False
                toc += f'<li><a href="#{anchor}">{heading.text}</a>'
                # Check if next heading is h3, if not close this li
                if i + 1 >= len(headings) or headings[i + 1].name != "h3":
                    toc += "</li>"
            elif heading.name == "h3":
                # Start a nested list if not already open
                if not nested_ul_open:
                    toc += "<ul>"
                    nested_ul_open = True
                toc += f'<li><a href="#{anchor}">{heading.text}</a></li>'
        # Close any open nested list at the end
        if nested_ul_open:
            toc += "</ul></li>"
        toc += "</ul>"
    return toc


class ContentPage(MarkdownRouteMixin, Page):
    show_in_menus_default = True
    subpage_types = ["core.ContentPage"]

    body = StreamField(CONTENT_BLOCKS)
    table_of_contents = models.TextField(blank=True)

    content_panels = [
        AITitleFieldPanel("title"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [index.SearchField("body")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        if self.live and self.show_in_menus:
            pages = Page.objects.live().in_menu()
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

    def save_revision(self, *args, **kwargs):
        self.table_of_contents = create_table_of_contents(self.body)
        return super().save_revision(*args, **kwargs)
