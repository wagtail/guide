from django.http import HttpResponseNotFound
from django.http.response import Http404
from django.template import loader

from apps.llms_txt.negotiation import (
    MARKDOWN_CONTENT_TYPE,
    patch_negotiated_response,
    prefers_markdown,
)


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
