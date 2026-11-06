from django.http import HttpResponse
from django.template import loader
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from .negotiation import (
    MARKDOWN_CONTENT_TYPE,
    patch_negotiated_response,
    prefers_markdown,
)


def estimate_tokens(content):
    """
    Rough token count for the `x-markdown-tokens` header, using the common
    ~4 characters per token heuristic. Agents only use it to budget context,
    so an estimate avoids pulling in a tokenizer.
    """
    return max(1, round(len(content) / 4))


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

        response = RoutablePageMixin.serve(self, request)
        if hasattr(response, "render"):
            response.render()
        converter = HTMLToMarkdownConverter(
            base_url=self.full_url, content_selector="body"
        )
        body = converter.convert(response.content.decode(response.charset))
        template = loader.get_template("llms_txt/page_from_html.md.jinja")
        context = {"page": self, "request": request, "frontmatter": True, "body": body}
        return template.render(context, request)

    def markdown_response(self, request):
        content = self.to_markdown_from_html(request)
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

        is_markdown = prefers_markdown(request)
        if is_markdown:
            response = self.markdown_response(request)
        else:
            response = super().serve(request, view, args, kwargs)

        patch_negotiated_response(response, is_markdown)
        return response
