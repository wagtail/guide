from contextvars import ContextVar
from typing import Annotated, TypedDict

from asgiref.sync import sync_to_async
from mcp.server.caching import CacheHint
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ToolAnnotations
from pydantic import Field

from . import services

# The Django request being served, set by the view for tools to use.
current_request = ContextVar("current_request")

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)

LocaleCode = Annotated[
    str | None,
    Field(
        description=(
            "Language code of the guide translation to use, such as 'en' or "
            "'fr'. Defaults to English."
        ),
        max_length=10,
    ),
]


class SearchResult(TypedDict):
    title: str
    search_description: str
    full_url: str
    parent_section: str


server = MCPServer(
    name="wagtail-guide",
    title="Wagtail Guide",
    instructions=(
        "The Wagtail user guide, for editors, moderators and administrators of "
        "Wagtail CMS sites. Search it with search_docs, then read pages with "
        "fetch_docs_page, citing their URLs. For developer questions, refer to "
        "https://docs.wagtail.org/ instead."
    ),
    website_url="https://guide.wagtail.org/",
    # Tools only change on deploy, so clients can cache the list, and there's
    # nothing to notify them of. Stateless requests under WSGI also can't hold
    # the long-lived `subscriptions/listen` stream open.
    cache_hints={"tools/list": CacheHint(ttl_ms=60 * 60 * 1000, scope="public")},
    subscriptions=False,
)


async def run_service(function, *args):
    """
    Run a synchronous service function, reporting its errors to the agent.

    Thread-sensitive by default: under the bridge view this runs on the
    request's own thread, so Django manages its database connection and active
    language as for any other view.
    """
    try:
        return await sync_to_async(function)(*args)
    except services.ServiceError as error:
        raise ToolError(str(error)) from error


def read_only_tool(**kwargs):
    """
    Register a read-only tool, described by its docstring as one paragraph.
    """

    def decorator(function):
        description = " ".join(function.__doc__.split())
        return server.tool(description=description, annotations=READ_ONLY, **kwargs)(
            function
        )

    return decorator


@read_only_tool()
async def search_docs(
    query: Annotated[str, Field(min_length=1, max_length=200)],
    limit: Annotated[int, Field(ge=1, le=20)] = 5,
    locale: LocaleCode = None,
) -> list[SearchResult]:
    """
    Search the Wagtail user guide. Returns matching pages with title,
    description, URL and parent section. Use whole words, as search terms
    aren't matched by prefix.
    """
    return await run_service(services.search_pages, query, limit, locale)


# Plain text rather than structured output, which would also send the
# Markdown JSON-escaped in the text content.
@read_only_tool(structured_output=False)
async def fetch_docs_page(
    url: Annotated[
        str,
        Field(
            min_length=1,
            max_length=500,
            description="URL or path of a guide page, such as a search_docs result.",
        ),
    ],
) -> str:
    """
    Fetch a page of the Wagtail user guide as Markdown, including its title,
    description and canonical URL.
    """
    return await run_service(services.get_page_markdown, current_request.get(), url)
