from django import template
from django.utils.translation import get_language
from wagtail.models import Page

from apps.core.models import FooterContent, HomePage

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

    version = get_version_from_language_code(page.locale.language_code)

    # Only get translations for the current version.
    translation_language_codes = (
        page.get_translations()
        .live()
        .filter(locale__language_code__endswith=version)
        .values_list("locale__language_code", flat=True)
    )

    return {
        "translations": [
            (get_language_from_language_code(lc), get_translation_url(page, lc))
            for lc in translation_language_codes
        ]
    }


@register.inclusion_tag("components/footer.html")
def footer():
    obj = FooterContent.objects.filter(locale__language_code=get_language()).first()
    if not obj:
        obj = FooterContent.objects.first()

    return {"footer": obj}


@register.simple_tag
def get_version_from_language_code(language_code):
    return language_code.rsplit("-", maxsplit=1)[1]


@register.simple_tag
def get_language_from_language_code(language_code):
    return language_code.rsplit("-", maxsplit=1)[0]
