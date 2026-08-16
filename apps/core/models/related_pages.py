from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel
from wagtail.models import Orderable


class RelatedPage(Orderable):
    source_page = ParentalKey(
        "wagtailcore.Page", related_name="related_pages", on_delete=models.CASCADE
    )
    related_page = models.ForeignKey(
        "wagtailcore.Page", related_name="+", on_delete=models.CASCADE
    )
    panels = [FieldPanel("related_page")]
