"""
Content negotiation between HTML and Markdown, for URLs that serve both.
"""

from django.utils.cache import patch_cache_control, patch_vary_headers

MARKDOWN_CONTENT_TYPE = "text/markdown;charset=utf-8"


def prefers_markdown(request):
    """
    Whether the client explicitly prefers Markdown over HTML.

    HTML wins ties (e.g. `Accept: */*`), so browsers and generic clients keep
    getting HTML.
    """
    preferred = request.get_preferred_type(["text/html", "text/markdown"])
    return preferred == "text/markdown"


def patch_negotiated_response(response, is_markdown):
    """
    Set the caching headers for a response chosen by `prefers_markdown`.
    """
    # The same URL serves HTML or Markdown, so caches must key on Accept.
    patch_vary_headers(response, ["Accept"])
    if is_markdown:
        # By default, Cloudflare ignores `Vary: Accept`, so a shared cache
        # could serve this Markdown to browsers. Keep it out of shared caches.
        patch_cache_control(response, private=True)
