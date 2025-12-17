from django.http import HttpResponse
from django.template import loader
from django.views.decorators.cache import cache_control
from wagtail.contrib.sitemaps import Sitemap


@cache_control(max_age=3600)
def llms_txt_view(request):
    pages = Sitemap(request).items()
    template = loader.get_template("llms_txt/llms.txt.jinja")
    context = {"pages": pages}
    content = template.render(context, request)
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    return response


@cache_control(max_age=3600)
def llms_full_txt_view(request):
    pages = Sitemap(request).items()
    template = loader.get_template("llms_txt/llms-full.txt.jinja")
    context = {"pages": pages}
    content = template.render(context, request)
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    return response
