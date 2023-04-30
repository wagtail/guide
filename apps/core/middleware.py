from django.conf import settings
from django.urls import LocalePrefixPattern
from django.utils.translation import activate, get_language

from apps.core.models import HomePage

pattern = LocalePrefixPattern()


class ValidateLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path == "/"
            or request.resolver_match
            and pattern.match(request.resolver_match.route)
        ):
            try:
                HomePage.objects.get(locale__language_code=get_language(), live=True)
                response = self.get_response(request)
            except HomePage.DoesNotExist:
                # The requested language is not available, use the default
                activate(settings.LANGUAGE_CODE)
                response = self.get_response(request)
        else:
            response = self.get_response(request)
        return response
