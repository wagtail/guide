import json

from bs4 import BeautifulSoup
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
        # Track the current state of nesting
        in_h2_li = False
        in_nested_ul = False

        for heading in headings:
            anchor = heading.attrs.get("id", slugify(heading.text))

            if heading.name == "h2":
                # If we were in a nested ul (under a previous h2), close it
                if in_nested_ul:
                    toc += "</ul>"
                    in_nested_ul = False

                # If we were in an h2 li, close it
                if in_h2_li:
                    toc += "</li>"

                # Start new h2 li
                toc += f'<li><a href="#{anchor}">{heading.text}</a>'
                in_h2_li = True

            elif heading.name == "h3":
                # If this H3 is the very first thing or we are strictly compliant,
                # it should be inside an LI.
                # If we are inside an h2_li, we can open a nested UL.
                if in_h2_li:
                    if not in_nested_ul:
                        toc += "<ul>"
                        in_nested_ul = True
                    toc += f'<li><a href="#{anchor}">{heading.text}</a></li>'
                else:
                    # Fallback for H3 at top level (orphaned)
                    toc += f'<li><a href="#{anchor}">{heading.text}</a></li>'

        # Cleanup at the end
        if in_nested_ul:
            toc += "</ul>"
        if in_h2_li:
            toc += "</li>"

        toc += "</ul>"
    return toc


class ContentPage(MarkdownRouteMixin, Page):
    show_in_menus_default = True
    subpage_types = ["core.ContentPage"]

    body = StreamField(CONTENT_BLOCKS)

    @property
    def table_of_contents(self):
        return create_table_of_contents(self.body)

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
