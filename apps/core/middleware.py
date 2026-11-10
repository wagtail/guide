import re
from urllib.parse import parse_qsl, urlencode

from django.shortcuts import redirect

PATTERN = re.compile(
    r"^/(?P<lang>[a-z-]+)-(?P<ver>latest|\d+\.\d+\.x|\d+\.x)(?P<rest>/.*)$"
)
DOCS_STYLE_LATEST_PATTERN = re.compile(r"^/(?P<lang>[a-z-]+)/latest(?P<rest>/.*)?$")


class VersionedUrlRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in ("GET", "HEAD"):
            return self.get_response(request)

        path = request.path_info
        query = dict(parse_qsl(request.META["QUERY_STRING"]))

        match = PATTERN.match(path)
        if match:
            lang = match.group("lang")
            ver = match.group("ver")
            rest = match.group("rest")
            query["target_version"] = ver
            new_url = f"/{lang}{rest}?{urlencode(query)}"
            return redirect(new_url)

        # Developer-docs-style URLs, e.g. `/en/latest/how-to-guides/`.
        match = DOCS_STYLE_LATEST_PATTERN.match(path)
        if match:
            lang = match.group("lang")
            rest = match.group("rest") or "/"
            new_url = f"/{lang}{rest}"
            if query:
                new_url = f"{new_url}?{urlencode(query)}"
            return redirect(new_url)

        return self.get_response(request)
