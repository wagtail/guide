from django.http import HttpResponse
from django.template import loader
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


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

    @route(r"^markdown/$", name="markdown")
    def markdown_view(self, request):
        return HttpResponse(
            self.to_markdown(request, frontmatter=True),
            content_type="text/markdown;charset=utf-8",
        )
