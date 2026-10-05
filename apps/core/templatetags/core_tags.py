import json

from django import template
from django.conf import settings
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


@register.inclusion_tag("components/hreflangs.html", takes_context=True)
def hreflangs(context):
    page = context.get("page")
    if not page:
        return {}

    # Each language version must list itself as well as all other versions,
    # using its own localised URL (slugs are translated per locale). A page can
    # be live and public yet have no URL (full_url is None) when it isn't
    # reachable through a site, so only list versions that resolve to a URL.
    translations = [page, *page.get_translations().live().public()]

    alternates = [
        (translation.locale.language_code, translation.full_url)
        for translation in translations
        if translation.full_url
    ]

    # Fallback for users whose language doesn't match any version: prefer the
    # default language, else fall back to this page's own URL when it has one.
    x_default = next(
        (
            url
            for language_code, url in alternates
            if language_code == settings.LANGUAGE_CODE
        ),
        page.full_url,
    )

    return {
        "translations": alternates,
        "x_default": x_default,
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
