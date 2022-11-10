from django.http import Http404
from django.utils.translation import activate, get_language

from apps.core.models import HomePage


class ValidateLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            HomePage.objects.get(locale__language_code=get_language(), live=True)
        except HomePage.DoesNotExist:
            activate('en-latest')
            raise Http404()
        response = self.get_response(request)
        return response
