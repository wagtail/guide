from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.llms_txt import views as llms_txt_views
from apps.search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path("llms.txt", llms_txt_views.llms_txt_view, name="llms_txt"),
    path("llms-full.txt", llms_txt_views.llms_full_txt_view, name="llms_full_txt"),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        # Add views for testing 404 and 500 templates
        path(
            "test404/",
            TemplateView.as_view(template_name="404.html"),
        ),
        path(
            "test500/",
            TemplateView.as_view(template_name="500.html"),
        ),
    ]

urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("search_json/", search_views.search_json, name="search_json"),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("", include(wagtail_urls)),
)


handler404 = "apps.core.views.page_not_found"
