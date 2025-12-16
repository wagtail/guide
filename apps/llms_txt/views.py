from django.http import HttpResponse
from django.template import loader
from wagtail.contrib.sitemaps import Sitemap


def llms_txt_view(request):
    pages = Sitemap().items()
    template = loader.get_template("llms_txt/llms_txt.html")
    context = {
        "pages": pages,
        "request": request,
    }
    content = template.render(context, request)
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    return response


def llms_full_txt_view(request):
    pages = Sitemap().items()
    template = loader.get_template("llms_txt/llms_full_txt.html")
    context = {
        "pages": pages,
        "request": request,
    }
    content = template.render(context, request)
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    return response
