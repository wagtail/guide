import json
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection, Locale, Page

from apps.core.factories import ContentPageFactory, HomePageFactory


class Command(BaseCommand):
    help = "Build development fixtures"

    locale = None
    home = None

    @staticmethod
    def cleanup_existing_data():
        Page.objects.exclude(path="0001").delete()
        Collection.objects.exclude(id=Collection.get_first_root_node().id).delete()
        get_image_model().objects.all().delete()
        get_document_model().objects.all().delete()

    def create_locale(self):
        self.locale, _ = Locale.objects.get_or_create(language_code="en-latest")

    def create_home_pages(self):
        self.home = HomePageFactory(locale=self.locale)
        for language_code, label in settings.LANGUAGES[1:]:
            locale, _ = Locale.objects.get_or_create(language_code=language_code)
            obj = self.home.copy_for_translation(locale)
            obj.title = f"{obj.title} {label}"
            obj.save_revision().publish()

    def create_content_pages(self):
        for title, subpage_titles in [
            [
                "Tutorial",
                ["Introduction", "Getting started", "Finding your way around"],
            ],
            ["How-to", ["Add a user", "Assign permissions" "Tag content"]],
            [
                "Explanation",
                [
                    "The Zen of Wagtail: Always wear the right hat",
                    "Customisations, why your site looks different",
                    "Rich text vs Streamfield blocks",
                ],
            ],
            [
                "Reference",
                [
                    "Dashboard",
                    "Page editor",
                    "Workflows",
                ],
            ],
        ]:
            page = ContentPageFactory(
                parent=self.home,
                title=title,
                slug=slugify(title),
            )
            for subpage_title in subpage_titles:
                ContentPageFactory(
                    parent=page,
                    title=subpage_title,
                    slug=slugify(subpage_title),
                )

            self.home.sections = json.dumps(
                [
                    {
                        "type": "section_grid",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "section": slugify(page.title),
                                    "title": page.title,
                                    "text": "text",
                                    "page": page.id,
                                },
                                "id": str(uuid.uuid4()),
                            }
                            for page in self.home.get_children()
                        ],
                        "id": "c990ba5e-645b-4bd9-89e0-1185ef22acb9",
                    }
                ]
            )
            self.home.save_revision().publish()

    def handle(self, *args, **options):
        self.stdout.write("Delete existing data.")
        self.cleanup_existing_data()

        self.stdout.write("Starting to build fixtures.")
        self.create_locale()

        self.create_home_pages()
        self.create_content_pages()

        self.stdout.write("Done building fixtures.")
