from django.db import models
from wagtail.models import Page


class Feedback(models.Model):
    feedback = models.CharField(
        choices=[
            ("happy", ":)"),
            ("unhappy", ":("),
        ],
        max_length=7,
    )

    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    feedback_text = models.TextField(blank=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback items"

    def __str__(self):
        return self.feedback
