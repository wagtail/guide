from django.http import HttpResponseNotFound
from django.template import loader
from wagtail.models import Site

from apps.llms_txt.negotiation import (
    MARKDOWN_CONTENT_TYPE,
    patch_negotiated_response,
    prefers_markdown,
)


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


def preview_page_not_found(request, path=""):
    """
    Render the 404 handler as if `path` was not found, for local development.
    """
    return render_page_not_found(request, path)
