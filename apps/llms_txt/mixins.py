from django.http import HttpResponse
from django.template import loader
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


class MarkdownRouteMixin(RoutablePageMixin):
    """Mixin to add Markdown rendering capability to Wagtail pages."""

    @property
    def has_markdown_route(self):
        """Check if this page has a markdown route."""
        return True

    def to_markdown(self, request=None):
        template = loader.get_template("llms_txt/markdown.html")
        context = {
            "page": self,
            "request": request,
        }
        return template.render(context, request)

    @route(r"^markdown/$", name="markdown")
    def markdown_view(self, request):
        return HttpResponse(
            self.to_markdown(request), content_type="text/markdown; charset=utf-8"
        )
