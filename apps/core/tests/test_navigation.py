from django.template import Context, Template
from django.test import TestCase
from django.utils import translation
from wagtail.core.models import Page

from apps.core.factories import HomePageFactory


class TestNavigation(TestCase):
    def setUp(self):
        self.home = HomePageFactory()
        self.a = Page(title="a", slug="a", show_in_menus=True)
        self.home.add_child(instance=self.a)
        self.ab = Page(title="ab", slug="ab", show_in_menus=True)
        self.a.add_child(instance=self.ab)
        self.ac = Page(title="ac", slug="ac", show_in_menus=True)
        self.a.add_child(instance=self.ac)
        self.b = Page(title="b", slug="b", show_in_menus=True)
        self.home.add_child(instance=self.b)

    def test_get_annotated_list_qs(self):
        pages = (
            Page.objects.descendant_of(self.home)
            .filter(depth__gt=2, depth__lte=4)
            .live()
            .in_menu()
        )
        result = Page.get_annotated_list_qs(pages)
        expected = [
            (self.a, {"close": [], "level": 0, "open": True}),
            (self.ab, {"close": [], "level": 1, "open": True}),
            (self.ac, {"close": [0], "level": 1, "open": False}),
            (self.b, {"close": [0], "level": 0, "open": False}),
        ]
        self.assertEqual(result, expected)

    def test_navigation_inclusion_tag(self):
        # A normal request will go through LocaleMiddleware to activate the locale.
        translation.activate(self.home.locale.language_code)
        template = Template("{% load core_tags %}{% navigation %}")
        result = template.render(Context({}))
        expected = """
            <nav>
              <ul class="navigation">
                <li class="navigation__item">
                  <a href="/en-latest/a/"
                     class="navigation__link navigation__link--large">a</a>
                  <ul class="navigation">
                    <li class="navigation__item">
                      <a href="/en-latest/a/ab/" class="navigation__link">ab</a>
                    </li>
                    <li class="navigation__item">
                      <a href="/en-latest/a/ac/" class="navigation__link">ac</a>
                    </li>
                  </ul>
                </li>
                <li class="navigation__item">
                  <a href="/en-latest/b/"
                     class="navigation__link navigation__link--large">b</a>
                </li>
              </ul>
            </nav>
        """
        self.assertHTMLEqual(result, expected)
