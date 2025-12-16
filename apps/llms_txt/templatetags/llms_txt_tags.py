from django import template

from apps.llms_txt.rich_text import richtext_markdown

register = template.Library()

register.filter("richtext_markdown", richtext_markdown)
