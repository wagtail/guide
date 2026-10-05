import json

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from wagtail.models import Page

from apps.core.models import FooterContent, HomePage
from apps.core.structured_data import build_graph

register = template.Library()


@register.inclusion_tag("components/header.html", takes_context=True)
def header(context):
    home = HomePage.objects.filter(locale__language_code=get_language()).first()

    # Translation may not have been activated (e.g. accessing the root path)
    if not home:
        home = HomePage.objects.first()

    pages = (
        Page.objects.descendant_of(home)
        .filter(depth__gt=2, depth__lte=4)
        .live()
        .public()
        .in_menu()
    )
    return {
        "site_title": home.title,
        "current_page": context.get("page"),
        "annotated_list": Page.get_annotated_list_qs(pages),
    }


@register.simple_tag
def get_translation_url(page, language_code):
    return page.full_url.replace(
        f"/{page.locale.language_code}/",
        f"/{language_code}/",
        1,
    )


@register.inclusion_tag("components/hreflangs.html", takes_context=True)
def hreflangs(context):
    page = context.get("page")
    if not page:
        return {}

    translation_language_codes = (
        page.get_translations()
        .live()
        .public()
        .values_list("locale__language_code", flat=True)
    )

    return {
        "translations": [
            (lc, get_translation_url(page, lc)) for lc in translation_language_codes
        ]
    }


@register.inclusion_tag("components/language_selector.html", takes_context=True)
def language_selector(context):
    page = context.get("page")
    if not page:
        return {"page": None, "translations": []}

    translations = page.get_translations().live().select_related("locale")
    return {
        "page": page,
        "request": context.get("request"),
        "translations": translations,
        "LANGUAGE_CODE": get_language(),
    }


@register.inclusion_tag("components/footer.html")
def footer():
    obj = FooterContent.objects.filter(locale__language_code=get_language()).first()
    if not obj:
        obj = FooterContent.objects.first()

    return {"footer": obj}


# Same escapes as Django's json_script, so content can't close the script tag.
JSON_SCRIPT_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


@register.simple_tag(takes_context=True)
def structured_data(context, site):
    if not site:
        return ""

    data = build_graph(site, page=context.get("page"), request=context.get("request"))
    payload = json.dumps(data).translate(JSON_SCRIPT_ESCAPES)
    return format_html(
        '<script type="application/ld+json">{}</script>', mark_safe(payload)
    )
