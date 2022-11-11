from django.http import Http404
from django.urls import LocalePrefixPattern
from django.utils.translation import activate, get_language

from apps.core.models import HomePage

pattern = LocalePrefixPattern()


class ValidateLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.resolver_match:
            # Check if the path is in the i18n_patterns
            if pattern.match(request.resolver_match.route):
                try:
                    HomePage.objects.get(
                        locale__language_code=get_language(), live=True)
                except HomePage.DoesNotExist:
                    # Activate English so that we have a site menu
                    activate("en-latest")
                    raise Http404()
        return response
