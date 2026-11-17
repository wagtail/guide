from django.http import HttpResponse
from django.template import loader
from django.test import RequestFactory
from django.utils.cache import patch_cache_control
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.models import Site

from .negotiation import MARKDOWN_CONTENT_TYPE


def estimate_tokens(content):
    """
    Rough token count for the `x-markdown-tokens` header, using the common
    ~4 characters per token heuristic. Agents only use it to budget context,
    so an estimate avoids pulling in a tokenizer.
    """
    return max(1, round(len(content) / 4))


class MarkdownRouteMixin(RoutablePageMixin):
    """Mixin to add Markdown rendering capability to Wagtail pages."""

    response_media_types = ["text/html", "text/markdown"]

    def get_vary_headers(self, request):
        headers = super().get_vary_headers(request)
        match = getattr(request, "routable_resolver_match", None)
        # Subroutes such as /markdown/ always return the same representation.
        if match and match.url_name != "index_route" and "Accept" in headers:
            headers.remove("Accept")
        return headers

    @property
    def has_markdown_route(self):
        """Check if this page has a markdown route."""
        return True

    def get_cached_paths(self):
        """
        Purge the markdown route along with the page, when the page changes.
        """
        return super().get_cached_paths() + ["/markdown/"]

    def to_markdown(self, request=None, frontmatter=False):
        """
        Render this page as Markdown.

        `frontmatter` prepends extra information when rendering pages standalone.
        """
        template = loader.get_template("llms_txt/page.md.jinja")
        # Resolve the site for rendering without a request object.
        if request is None:
            request = RequestFactory().get("/")
            request.site = self.get_site()
        context = {
            "page": self,
            "frontmatter": frontmatter,
        }
        return template.render(context, request)

    def to_markdown_from_html(self, request):
        """
        Render this page as Markdown, converted from the page's own HTML.

        Unlike `to_markdown`, this keeps everything visitors see around the
        content, like the "In this section" lists of section pages and links
        to llms.txt. The navigation menu is left out by the converter, and
        elements with `data-markdown-ignore` are too.
        """
        # Wagtail's converter imports rich text features, which need the app
        # registry, and models import this module before it's ready.
        from wagtail.admin.rich_text.converters.html_markdown import (
            HTMLToMarkdownConverter,
        )

        response = self.render(request)
        response.render()
        converter = HTMLToMarkdownConverter(
            base_url=self.full_url, content_selector="main"
        )
        body = converter.convert(response.content.decode(response.charset))
        template = loader.get_template("llms_txt/page_from_html.md.jinja")
        context = {
            "page": self,
            "request": request,
            "frontmatter": True,
            "body": body,
            "sitemap_pages": self.get_sitemap_pages(request),
        }
        return template.render(context, request)

    def get_sitemap_pages(self, request):
        """
        The other pages of the site, listed after the page in its Markdown.

        Same pages and order as llms.txt, so agents crawling from any page can
        discover the rest of the site without fetching llms.txt first.
        """
        site = Site.find_for_request(request)
        pages = (
            site.root_page.get_descendants(inclusive=True)
            .live()
            .public()
            .exclude(pk=self.pk)
            .order_by("path")
        )
        # Fetch specific page models last: `exclude()` and a `Site.root_page`
        # that is the base Page (as when a site object is cached in memory)
        # both yield pages without their subclass methods.
        return pages.specific()

    def markdown_response(self, request):
        content = self.to_markdown_from_html(request)
        response = HttpResponse(content, content_type=MARKDOWN_CONTENT_TYPE)
        response["x-markdown-tokens"] = estimate_tokens(content)
        return response

    @route(r"^markdown/$", name="markdown")
    def markdown_view(self, request):
        return self.markdown_response(request)

    @route(r"^$", name="index_route")
    def index_route(self, request, *args, **kwargs):
        if self.get_response_media_type(request) == "text/markdown":
            response = self.markdown_response(request)
            # Cloudflare ignores Vary: Accept by default. Keep negotiated
            # Markdown out of shared caches, as on the 404 page.
            patch_cache_control(response, private=True)
            return response
        return super().index_route(request, *args, **kwargs)
