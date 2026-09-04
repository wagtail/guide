import re
from urllib.parse import parse_qsl, urlencode

from django.shortcuts import redirect

PATTERN = re.compile(
    r"^/(?P<lang>[a-z-]+)-(?P<ver>latest|\d+\.\d+\.x|\d+\.x)(?P<rest>/.*)$"
)


class VersionedUrlRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        match = PATTERN.match(path)

        if match and request.method in ("GET", "HEAD"):
            lang = match.group("lang")
            ver = match.group("ver")
            rest = match.group("rest")
            query = dict(parse_qsl(request.META["QUERY_STRING"]))
            query["target_version"] = ver
            new_url = f"/{lang}{rest}?{urlencode(query)}"
            return redirect(new_url)

        return self.get_response(request)
