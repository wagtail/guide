from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Locale, Page


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        search_results = (
            Page.objects.live()
            .public()
            .filter(locale=Locale.get_active())
            .search(search_query)
        )
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "SEO_NOINDEX": True,
        },
    )


# Sections are the children of each locale's homepage, under the tree root.
SECTION_DEPTH = 3


def get_section_path(page):
    return page.path[: Page.steplen * SECTION_DEPTH]


def get_section_titles(pages):
    """Titles of the sections the pages are in, keyed by section path."""
    paths = {get_section_path(page) for page in pages if page.depth > SECTION_DEPTH}
    return dict(Page.objects.filter(path__in=paths).values_list("path", "title"))


class PageSerializer(serializers.ModelSerializer):
    full_url = serializers.SerializerMethodField("get_full_url")
    parent_section = serializers.SerializerMethodField("get_parent_section")

    class Meta:
        model = Page
        fields = ["id", "title", "search_description", "full_url", "parent_section"]

    def get_full_url(self, page):
        # With the request, Wagtail looks up the site root paths once for all
        # results, rather than once per result.
        return page.get_full_url(self.context["request"])

    def get_parent_section(self, page):
        if page.depth > SECTION_DEPTH:
            return self.context["section_titles"][get_section_path(page)]
        else:
            return _("Home")


@api_view(["GET"])
def search_json(request):
    if search_query := request.GET.get("query"):
        search_results = (
            Page.objects.live()
            .public()
            .filter(locale=Locale.get_active())
            .autocomplete(search_query)
        )
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()
    # Look up all the parent sections at once, rather than once per result.
    search_results = list(search_results)
    serializer = PageSerializer(
        search_results,
        many=True,
        context={
            "request": request,
            "section_titles": get_section_titles(search_results),
        },
    )
    return Response(serializer.data)
