from django.http import HttpResponseNotFound
from django.http.response import Http404
from django.template import loader
from django.utils.cache import patch_cache_control, patch_vary_headers


class Custom404(Http404):
    def __init__(self, *args, fallback_pages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fallback_pages = fallback_pages


def page_not_found(request, exception):
    # HTML is listed first so it wins ties, e.g. for `Accept: */*`.
    preferred_type = request.get_preferred_type(["text/html", "text/markdown"])
    if preferred_type == "text/markdown":
        body = loader.get_template("llms_txt/404.md.jinja").render({}, request)
        response = HttpResponseNotFound(
            body, content_type="text/markdown;charset=utf-8"
        )
        # Cloudflare ignores `Vary: Accept`, so a shared cache could serve
        # this Markdown to browsers. Keep it out of shared caches.
        patch_cache_control(response, private=True)
    else:
        context = {"fallback_pages": getattr(exception, "fallback_pages", None)}
        body = loader.get_template("404.html").render(context, request)
        response = HttpResponseNotFound(body)

    patch_vary_headers(response, ["Accept"])
    return response
