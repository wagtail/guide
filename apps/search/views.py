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
            Page.objects.live().filter(locale=Locale.get_active()).search(search_query)
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


class PageSerializer(serializers.ModelSerializer):
    parent_section = serializers.SerializerMethodField("get_parent_section")

    class Meta:
        model = Page
        fields = ["id", "title", "search_description", "full_url", "parent_section"]

    def get_parent_section(self, page):
        # We might update this to search for the first SectionPage
        ancestors = page.get_ancestors()
        if len(ancestors) >= 3:
            return ancestors[2].title
        else:
            return _("Home")  # Shouldn't this be None? OR a dash?


@api_view(["GET"])
def search_json(request):
    if search_query := request.GET.get("query"):
        search_results = (
            Page.objects.live()
            .filter(locale=Locale.get_active())
            .autocomplete(search_query)
        )
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()
    serializer = PageSerializer(search_results, many=True)
    return Response(serializer.data)
