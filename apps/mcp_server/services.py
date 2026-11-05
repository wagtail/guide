from urllib.parse import urlsplit

from django.conf import settings
from django.http import Http404
from django.utils import translation
from wagtail.models import Locale, Page, Site

from apps.core.views import get_fallback_pages
from apps.search.views import PageSerializer


class SearchResultSerializer(PageSerializer):
    """The site search's JSON results, without page IDs agents have no use for."""

    class Meta(PageSerializer.Meta):
        fields = [field for field in PageSerializer.Meta.fields if field != "id"]


class ServiceError(Exception):
    """An error whose message is meant for the agent calling the tool."""


def get_locale(language_code):
    try:
        return Locale.objects.get(language_code=language_code or settings.LANGUAGE_CODE)
    except Locale.DoesNotExist:
        available = Locale.objects.values_list("language_code", flat=True)
        raise ServiceError(
            f"Unknown locale {language_code!r}. Available: {', '.join(available)}."
        )


def search_pages(query, limit, language_code=None):
    # Unlike the site search, this doesn't record a hit for the query, so
    # agent traffic stays out of the editors' search promotion stats. It also
    # matches any of the words rather than all of them, as agents search with
    # phrases rather than keywords, and pages matching more words rank first.
    pages = (
        Page.objects.live()
        .public()
        .filter(locale=get_locale(language_code))
        .search(query, operator="or")[:limit]
    )
    return SearchResultSerializer(pages, many=True).data


def get_page_path(request, url):
    """The path of `url` on this site, rejecting URLs of other sites."""
    parts = urlsplit(url)
    if parts.netloc:
        hostnames = Site.objects.values_list("hostname", flat=True)
        if parts.hostname not in {request.get_host().split(":")[0], *hostnames}:
            raise ServiceError(f"{url} is not a page of this site.")
    # Routing also resolves the `markdown/` URLs linked from llms.txt.
    return parts.path or "/"


def find_page(request, path):
    """The live page at `path`, as Wagtail would serve it."""
    language_code = translation.get_language_from_path(path) or settings.LANGUAGE_CODE
    if path.startswith(f"/{language_code}/"):
        page_path = path.removeprefix(f"/{language_code}")
    else:
        page_path = path
    components = [component for component in page_path.split("/") if component]

    with translation.override(language_code):
        site = Site.find_for_request(request)
        root_page = site.root_page.localized.specific
        try:
            page = Page.route(root_page, request, components).page
        except Http404:
            fallback_pages = get_fallback_pages(request, page_path)
            return None, fallback_pages
    return page, []


def get_page_markdown(request, url):
    page, fallback_pages = find_page(request, get_page_path(request, url))
    # `Page.route()` checks the page is live, but not its privacy settings.
    if page is None or page.get_view_restrictions().exists():
        message = f"No page found at {url}."
        if fallback_pages:
            urls = ", ".join(page.full_url for page in fallback_pages)
            message += f" It exists in other languages: {urls}"
        raise ServiceError(message)

    page = page.specific
    if not hasattr(page, "to_markdown"):
        raise ServiceError(f"{url} has no Markdown version.")

    return page.to_markdown(request, frontmatter=True)
