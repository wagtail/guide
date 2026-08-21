from django_ai_core.contrib.agents import registry as agent_registry
from django_ai_core.contrib.index import registry as index_registry
from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.models import Page
from wagtail_ai.agents.suggested_content import MAX_LIMIT, SuggestedContentAgent

from apps.core.vector_indexes import render_first_paragraph


@agent_registry.register()
class LocalizedSuggestedContentAgent(SuggestedContentAgent):
    """
    Suggests related content using the page's own title, search
    description, and a short body snippet as the search query (instead of
    the raw preview text), and restricts suggestions to the current page's
    locale.
    """

    slug = "wai_suggested_content"
    BODY_SNIPPET_LENGTH = 300

    def execute(
        self,
        vector_index: str,
        exclude_pks: list[str],
        content: str,
        limit: int = 3,
        chunk_size: int = 1000,
    ) -> list:
        locale = None
        current_page = None
        if exclude_pks:
            try:
                current_page = Page.objects.get(pk=exclude_pks[0])
                if current_page.locale:
                    locale = current_page.locale.language_code
            except Page.DoesNotExist:
                pass

        if current_page is not None:
            specific = current_page.specific
            query_parts = [specific.title]

            description = getattr(specific, "search_description", "") or ""
            if description:
                query_parts.append(description)

            if hasattr(specific, "body"):
                body_snippet = render_first_paragraph(specific)
                if body_snippet:
                    query_parts.append(body_snippet[: self.BODY_SNIPPET_LENGTH])

            query = ". ".join(query_parts)
        else:
            query = content[:chunk_size] if content else ""

        if not query:
            return []

        index_cls = index_registry.get(vector_index)
        index = index_cls()
        finder = AdminURLFinder()

        extended_limit = limit + len(exclude_pks)
        if extended_limit > MAX_LIMIT:
            return []

        return [
            {
                "id": str(page.pk),
                "title": page.title,
                "editUrl": finder.get_edit_url(page),
            }
            for page in index.search_sources(query, locale=locale)[:extended_limit]
            if str(page.pk) not in exclude_pks
        ][:limit]
