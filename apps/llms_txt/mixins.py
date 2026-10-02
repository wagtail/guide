from django.http import HttpResponse
from django.template import loader
from django.utils.cache import patch_cache_control, patch_vary_headers
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

MARKDOWN_CONTENT_TYPE = "text/markdown;charset=utf-8"


def estimate_tokens(content):
    """
    Rough token count for the `x-markdown-tokens` header, using the common
    ~4 characters per token heuristic. Agents only use it to budget context,
    so an estimate avoids pulling in a tokenizer.
    """
    return max(1, round(len(content) / 4))


def prefers_markdown(request):
    """
    Whether the client explicitly prefers Markdown over HTML.

    HTML wins ties (e.g. `Accept: */*`), so browsers and generic clients keep
    getting the HTML page.
    """
    preferred = request.get_preferred_type(["text/html", "text/markdown"])
    return preferred == "text/markdown"


class MarkdownRouteMixin(RoutablePageMixin):
    """Mixin to add Markdown rendering capability to Wagtail pages."""

    @property
    def has_markdown_route(self):
        """Check if this page has a markdown route."""
        return True

    def to_markdown(self, request=None, frontmatter=False):
        """
        Render this page as Markdown.

        `frontmatter` prepends a YAML metadata block. It is only wanted when a
        page is served on its own: llms-full.txt concatenates every page into
        one document, where repeated `---` blocks partway down would be
        malformed.
        """
        template = loader.get_template("llms_txt/page.md.jinja")
        context = {
            "page": self,
            "request": request,
            "frontmatter": frontmatter,
        }
        return template.render(context, request)

    def markdown_response(self, request):
        content = self.to_markdown(request, frontmatter=True)
        response = HttpResponse(content, content_type=MARKDOWN_CONTENT_TYPE)
        response["x-markdown-tokens"] = estimate_tokens(content)
        return response

    @route(r"^markdown/$", name="markdown")
    def markdown_view(self, request):
        return self.markdown_response(request)

    def serve(self, request, view=None, args=None, kwargs=None):
        # Content negotiation applies to the page URL itself, not other routes.
        if view is not None and view != self.index_route:
            return super().serve(request, view, args, kwargs)

        if prefers_markdown(request):
            response = self.markdown_response(request)
            # Cloudflare ignores `Vary: Accept`, so a shared cache could serve
            # this Markdown to browsers. Keep it out of shared caches.
            patch_cache_control(response, private=True)
        else:
            response = super().serve(request, view, args, kwargs)

        # The same URL serves HTML or Markdown, so caches must key on Accept.
        patch_vary_headers(response, ["Accept"])
        return response
