from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.documents.models import AbstractDocument
from wagtail.images.models import AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    """Custom Image model"""


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage,
        on_delete=models.CASCADE,
        related_name="renditions",
        verbose_name=_("image"),
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class CustomDocument(AbstractDocument):
    """Custom Document model"""
