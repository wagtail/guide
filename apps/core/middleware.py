from django.shortcuts import get_object_or_404
from django.utils.translation import get_language

from apps.core.models import HomePage


class ValidateLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        get_object_or_404(HomePage, locale__language_code=get_language(), live=True)
        response = self.get_response(request)
        return response
