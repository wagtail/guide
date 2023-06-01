from django.conf import settings
from django.shortcuts import redirect
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
                is_available_for_user_lang = HomePage.objects.filter(
                    locale__language_code=get_language(), live=True
                ).exists()

                if not is_available_for_user_lang:
                    # fallback to default language where home page is available
                    activate(settings.LANGUAGE_CODE)
                    home = HomePage.objects.get(
                        locale__language_code=settings.LANGUAGE_CODE, live=True
                    )
                    return redirect(home.get_url(request))
        return response
