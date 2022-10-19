import json

from bs4 import BeautifulSoup
from django.db import models
from django.http import HttpResponse
from django.template import Context, Template
from django.template.defaultfilters import slugify
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel
from wagtail.core.fields import StreamField
from wagtail.models import Page

from apps.core.models.feedback import Feedback

from ..blocks import CONTENT_BLOCKS


class ContentPageForm(WagtailAdminPageForm):
    def create_table_of_contents(self, body):
        template = Template("{% load wagtailcore_tags %}{% include_block body %}")
        content = template.render(Context({"body": body}))
        soup = BeautifulSoup(content, "lxml")
        headings = soup.select("h2,h3")
        toc = ""
        if headings:
            toc += "<ul>"
            for heading in headings:
                toc += f'<li><a href="#{slugify(heading.text)}">{heading.text}</a></li>'  # noqa
            toc += "</ul>"
        self.instance.table_of_contents = toc

    def clean(self):
        cleaned_data = super().clean()
        body = cleaned_data["body"]
        self.create_table_of_contents(body)
        return cleaned_data


class ContentPage(Page):
    show_in_menus_default = True
    subpage_types = ["core.ContentPage"]

    body = StreamField(
        CONTENT_BLOCKS,
        use_json_field=True,
    )
    table_of_contents = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("body")]
    base_form_class = ContentPageForm

    def get_context(self, request, *args, **kwargs):
        if self.live and self.show_in_menus:
            context = super().get_context(request, *args, **kwargs)
            pages = Page.objects.live().in_menu()
            context.update(
                previous=pages.filter(path__lt=self.path).last(),
                next=pages.filter(path__gt=self.path).first(),
            )
            return context

    def serve(self, request):
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
            return super().serve(request)
