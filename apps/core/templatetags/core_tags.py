from django import template
from django.utils.translation import get_language
from wagtail.core.models import Page

from apps.core.models import HomePage

register = template.Library()


@register.inclusion_tag("components/navigation.html", takes_context=True)
def navigation(context):
    home = HomePage.objects.filter(locale__language_code=get_language()).first()
    pages = (
        Page.objects.descendant_of(home)
        .filter(depth__gt=2, depth__lte=4)
        .live()
        .in_menu()
    )
    return {
        "current_page": context.get("page"),
        "annotated_list": Page.get_annotated_list_qs(pages),
    }
