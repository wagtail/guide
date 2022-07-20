import json

import factory
import wagtail_factories
from django.conf import settings
from django.utils import timezone
from faker import Faker
from wagtail.core.models import Locale, Page, Site

from apps.core.models import ContentPage, HomePage

fake = Faker()
Faker.seed(0)


class LocaleFactory(factory.django.DjangoModelFactory):
    language_code = settings.LANGUAGE_CODE

    class Meta:
        model = Locale
        django_get_or_create = ("language_code",)


class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HomePage

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        home = HomePage.objects.first()
        if not home:
            root = Page.get_first_root_node()
            home = HomePage(title="Using Wagtail: an Editor's guide", slug="home-x")
            root.add_child(instance=home)
            site = Site.objects.first()
            if site:
                old_home = site.root_page
                site.root_page = home
                site.save()
                old_home.delete()
            else:
                if settings.DEBUG:
                    hostname = "127.0.0.1"
                    port = 8000
                else:
                    hostname = settings.ALLOWED_HOSTS[0]
                    port = 443
                Site.objects.create(
                    hostname=hostname,
                    is_default_site=True,
                    root_page=home,
                    port=port,
                )
        return home


class ContentPageFactory(wagtail_factories.PageFactory):
    title = factory.Sequence(lambda n: "Page {}".format(n))
    locale = factory.SubFactory(LocaleFactory)

    class Meta:
        model = ContentPage

    @factory.lazy_attribute
    def body(self):
        return json.dumps(
            [
                {"type": "text", "value": f"<p>{ fake.paragraph() }</p>"},
            ],
        )

    @factory.lazy_attribute
    def first_published_at(self):
        return timezone.now()

    @factory.lazy_attribute
    def parent(self):
        return HomePageFactory()
