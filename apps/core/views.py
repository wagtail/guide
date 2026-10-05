from django.http import HttpResponseNotFound, JsonResponse
from django.template import loader
from django.urls import reverse
from wagtail.models import Site

from apps.llms_txt.negotiation import (
    MARKDOWN_CONTENT_TYPE,
    patch_negotiated_response,
    prefers_markdown,
)

# The API catalog lists the site's public API endpoints, per RFC 9727. Only
# anonymously-readable v3 API resources are advertised here: the write and
# authenticated endpoints are intentionally left out, since agents browsing
# the catalog can't use them without credentials.
API_CATALOG_PROFILE = "https://www.rfc-editor.org/info/rfc9727"
API_CATALOG_CONTENT_TYPE = f'application/linkset+json; profile="{API_CATALOG_PROFILE}"'
OPENAPI_CONTENT_TYPE = "application/vnd.oai.openapi+json;version=3.1"


def api_catalog(request):
    """Serve the API catalog document (RFC 9727) for the public v3 API."""
    root_url = request.build_absolute_uri("/").rstrip("/")

    linkset = {
        "linkset": [
            {
                "anchor": f"{root_url}{reverse('wagtailapi_v3:list_pages')}",
                "item": [
                    {"href": f"{root_url}{reverse('wagtailapi_v3:list_pages')}"},
                ],
                "service-desc": [
                    {
                        "href": f"{root_url}{reverse('wagtailapi_v3:openapi-json')}",
                        "type": OPENAPI_CONTENT_TYPE,
                    }
                ],
                "service-doc": [
                    {
                        "href": f"{root_url}{reverse('wagtailapi_v3:openapi-view')}",
                        "type": "text/html",
                    }
                ],
            },
        ]
    }
    response = JsonResponse(
        linkset,
        content_type=API_CATALOG_CONTENT_TYPE,
        json_dumps_params={"indent": 2},
    )
    return response


def get_fallback_pages(request, path):
    """
    Pages at `path` in other locales.

    Wagtail swallows exceptions raised while routing and raises a plain
    `Http404`, so these are looked up here rather than attached to it.
    """
    site = Site.find_for_request(request)
    if site is None:
        return []

    root_page = site.root_page.localized.specific
    if not hasattr(root_page, "get_fallback_pages"):
        return []

    path_components = [component for component in path.split("/") if component]
    return root_page.get_fallback_pages(request, path_components)


def get_page_path(request):
    """
    The page path for 404s raised from Wagtail's serve view, else `None`.
    """
    match = request.resolver_match
    if match is None or match.url_name != "wagtail_serve":
        return None
    # Wagtail's serve URL pattern captures the page path as its only argument.
    return match.args[0]


def render_page_not_found(request, path=None):
    fallback_pages = get_fallback_pages(request, path) if path is not None else []
    context = {"fallback_pages": fallback_pages}
    is_markdown = prefers_markdown(request)
    if is_markdown:
        body = loader.get_template("llms_txt/404.md.jinja").render(context, request)
        response = HttpResponseNotFound(body, content_type=MARKDOWN_CONTENT_TYPE)
    else:
        body = loader.get_template("404.html").render(context, request)
        response = HttpResponseNotFound(body)

    patch_negotiated_response(response, is_markdown)
    return response


def page_not_found(request, exception):
    return render_page_not_found(request, get_page_path(request))
