from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


class HomePage(Page):
    subpage_types = ["content.ContentPage"]
    max_count = 1
    tutorial_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )
    how_to_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )
    explanation_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )
    reference_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("tutorial_image"),
        FieldPanel("how_to_image"),
        FieldPanel("explanation_image"),
        FieldPanel("reference_image"),
    ]
