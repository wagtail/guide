from http import HTTPStatus

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.core.factories import HomePageFactory, LocaleFactory


class TestValidateLocaleMiddleware(TestCase):
    """
    LocaleMiddleware tries to determine the user’s language preference by following
    this algorithm:

    1. First, it looks for the language prefix in the requested URL.
    2. Failing that, it looks for a cookie, named `django_language`.
    3. Failing that, it looks at the Accept-Language HTTP header. This header is sent by
       your browser and tells the server which language(s) you prefer, in order by
       priority. Django tries each language in the header until it finds one with
       available translations.
    4. Failing that, it uses the global LANGUAGE_CODE setting.

    Wagtail Guide has all languages in LANGUAGES setting, therefore LocaleMiddleware
    will redirect to any language prefix URL. Unfortunately, Wagtail might not have
    the corresponding homepage for that language published. If Wagtail has no
    homepage available for the requested language, it raises a 404.

    This behaviour is undesirable. As step 3 of the algoritm will end up in a 404.
    To resolve this issue, we introduce our ValidateLocaleMiddleware.

    ValidateLocaleMiddleware checks for a published homepage for the requested language.
    If it does not exist, it falls back to English. The default, and always published
    language/homepage.

    The ValidateLocaleMiddleware kicks in on `/` and any i18n pattern.
    Other URLs are ignored, and have the default LocaleMiddleware behaviour.
    """

    def setUp(self):
        self.en = LocaleFactory(language_code="en-latest")
        self.home_en = HomePageFactory(locale=self.en)

    def test_middleware_settings(self):
        self.assertIn("django.middleware.locale.LocaleMiddleware", settings.MIDDLEWARE)
        self.assertIn(
            "apps.core.middleware.ValidateLocaleMiddleware", settings.MIDDLEWARE
        )
        self.assertGreater(
            settings.MIDDLEWARE.index("apps.core.middleware.ValidateLocaleMiddleware"),
            settings.MIDDLEWARE.index("django.middleware.locale.LocaleMiddleware"),
        )

    def test_request_root_redirects_to_language_code(self):
        self.assertEqual(settings.LANGUAGE_CODE, "en-latest")
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/en-latest/")
        self.assertEqual(self.client.get("/en-latest/").status_code, HTTPStatus.OK)

    def test_request_root_with_accept_language_header(self):
        # To English, if German doesn't exist
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/en-latest/")
        self.assertEqual(self.client.get("/en-latest/").status_code, HTTPStatus.OK)
        # To German, if German exists
        de = LocaleFactory(language_code="de-latest")
        self.home_de = self.home_en.copy_for_translation(locale=de)
        self.home_de.save_revision().publish()
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/de-latest/")
        self.assertEqual(self.client.get("/de-latest/").status_code, HTTPStatus.OK)

    def test_request_root_with_cookie(self):
        self.assertEqual(settings.LANGUAGE_COOKIE_NAME, "django_language")
        de = LocaleFactory(language_code="de-latest")
        self.home_de = self.home_en.copy_for_translation(locale=de)
        self.home_de.save_revision().publish()
        # The HTTP_ACCEPT_LANGUAGE is ignored, the cookie takes precedence
        self.client.cookies["django_language"] = "en-latest"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/en-latest/")
        self.assertEqual(self.client.get("/en-latest/").status_code, HTTPStatus.OK)

    def test_request_specific_url(self):
        de = LocaleFactory(language_code="de-latest")
        self.home_de = self.home_en.copy_for_translation(locale=de)
        self.home_de.save_revision().publish()
        # The HTTP_ACCEPT_LANGUAGE is ignored
        self.client.cookies["django_language"] = "de"
        # The HTTP_ACCEPT_LANGUAGE is ignored
        response = self.client.get("/en-latest/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_wagtail_admin_respects_accept_language(self):
        # Non i18n_patterns respect HTTP_ACCEPT_LANGUAGE
        url = reverse("wagtailadmin_login")
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        expected = "<h1>Inloggen in Wagtail</h1>"
        self.assertInHTML(expected, str(response.content))

    def test_django_admin_respects_accept_language(self):
        # Non i18n_patterns respect HTTP_ACCEPT_LANGUAGE
        url = reverse("admin:login")
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        expected = '<h1 id="site-name"><a href="/django-admin/">Django-beheer</a></h1>'
        self.assertInHTML(expected, str(response.content))

    def test_sitemap_xml(self):
        # Non i18n_patterns respect HTTP_ACCEPT_LANGUAGE
        url = "/sitemap.xml"
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        expected = (
            b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            b'xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        )
        self.assertIn(expected, response.content)
