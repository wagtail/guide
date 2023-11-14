from django.http import HttpResponseNotFound
from django.http.response import Http404
from django.template import loader


class Custom404(Http404):
    def __init__(self, *args, fallback_pages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fallback_pages = fallback_pages


def page_not_found(request, exception):
    context = {"fallback_pages": getattr(exception, "fallback_pages", None)}
    template = loader.get_template("404.html")
    body = template.render(context, request)
    return HttpResponseNotFound(body)
