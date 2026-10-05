from django.http import HttpResponseNotFound, JsonResponse
from django.http.response import Http404
from django.template import loader

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
    api_url = f"{root_url}/api/v3-preview"

    linkset = {
        "linkset": [
            {
                "anchor": f"{api_url}/",
                "item": [
                    {"href": f"{api_url}/pages/"},
                    {"href": f"{api_url}/redirects/"},
                    {"href": f"{api_url}/documents/"},
                    {"href": f"{api_url}/images/"},
                ],
                "service-desc": [
                    {
                        "href": f"{api_url}/openapi.json",
                        "type": OPENAPI_CONTENT_TYPE,
                    }
                ],
                "service-doc": [
                    {
                        "href": f"{api_url}/docs/",
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


class Custom404(Http404):
    def __init__(self, *args, fallback_pages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fallback_pages = fallback_pages


def page_not_found(request, exception):
    is_markdown = prefers_markdown(request)
    if is_markdown:
        body = loader.get_template("llms_txt/404.md.jinja").render({}, request)
        response = HttpResponseNotFound(body, content_type=MARKDOWN_CONTENT_TYPE)
    else:
        context = {"fallback_pages": getattr(exception, "fallback_pages", None)}
        body = loader.get_template("404.html").render(context, request)
        response = HttpResponseNotFound(body)

    patch_negotiated_response(response, is_markdown)
    return response
