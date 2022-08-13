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


@register.filter
def hreflang_url(value, arg):
    return value.replace(arg, "en-latest", 1)
  
  
@register.filter
def next_page(page):
    first_descendant = page.get_descendants().live().first()
    if first_descendant:
        return first_descendant

    next_sibling = page.get_siblings().live().filter(path__gt=page.path).first()
    if next_sibling:
        return next_sibling

    next_section = (
        page.get_ancestors()
        .live()
        .last()
        .get_siblings()
        .filter(path__gt=page.path)
        .first()
    )
    if next_section:
        return next_section

    return None


@register.filter
def previous_page(page):
    previous_page = page.get_siblings().live().filter(path__lt=page.path).last()
    if previous_page:
        last_descendant = previous_page.get_descendants().live().last()
        if last_descendant:
            return last_descendant
        return previous_page
    parent = page.get_ancestors().live().last()
    if parent:
        return parent

    return None
