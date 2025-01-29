import json
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from faker import Faker
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection, Locale, Page

from apps.core.factories import ContentPageFactory, HomePageFactory, SectionPageFactory

fake = Faker()


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
        self.locale, _ = Locale.objects.get_or_create(
            language_code=settings.LANGUAGE_CODE
        )

    def create_home_pages(self):
        self.home = HomePageFactory(locale=self.locale)
        languages = [
            ("en", "English"),
            ("nl", "Dutch"),
            # Make sure languages with region code is handled correctly
            ("pt-br", "Portuguese (Brazil)"),
        ]
        locales = [
            (f"{code}-{version}", f"{name} ({version})")
            for code, name in languages
            for version in settings.WAGTAIL_GUIDE_VERSIONS
        ]
        for language_code, label in locales[1:]:
            locale, _ = Locale.objects.get_or_create(language_code=language_code)
            obj = self.home.copy_for_translation(locale)
            obj.title = f"{obj.title} {label}"
            obj.save_revision().publish()

    def create_content_pages(self):
        for title, subpage_titles in [
            [
                "Tutorial",
                [
                    "Getting started",
                    "Dashboard",
                    "Page",
                    "Images",
                    "Documents",
                    "Search",
                ],
            ],
            [
                "How-to",
                [
                    "Add a user",
                    "Assign permissions",
                    "Create rich text",
                    "Work with collections",
                    "Tag content",
                    "Add a focus area to an image",
                    "Order pages",
                ],
            ],
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
                    "Glossary",
                    "Rich text shortcuts",
                    "Groups and permissions",
                    "Workflows",
                ],
            ],
        ]:
            page = SectionPageFactory(
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

        tutorial, how_to, explanation, reference = self.home.get_children()
        self.home.sections = json.dumps(
            [
                {
                    "type": "section_grid",
                    "value": [
                        {
                            "type": "item",
                            "value": {
                                "section": "tutorial",
                                "title": "Tutorial",
                                "text": "Our tutorials will help you learn and master "
                                "the different ways of creating and managing "
                                "content in Wagtail. It’s the best place to "
                                "get started.",
                                "page": tutorial.id,
                            },
                            "id": str(uuid.uuid4()),
                        },
                        {
                            "type": "item",
                            "value": {
                                "section": "how-to",
                                "title": "How-to",
                                "text": "Our how-to guides explain the simplest ways "
                                "to achieve common tasks.",
                                "page": how_to.id,
                            },
                            "id": str(uuid.uuid4()),
                        },
                        {
                            "type": "item",
                            "value": {
                                "section": "explanation",
                                "title": "Explanation",
                                "text": "Wagtail has strong opinions about CMS best "
                                "practices. This section describes why Wagtail "
                                "works how it does from a user’s perspective.",
                                "page": explanation.id,
                            },
                            "id": str(uuid.uuid4()),
                        },
                        {
                            "type": "item",
                            "value": {
                                "section": "reference",
                                "title": "Reference",
                                "text": "Our reference material gets to the point, "
                                "giving the key information at a glance.",
                                "page": reference.id,
                            },
                            "id": str(uuid.uuid4()),
                        },
                    ],
                    "id": "c990ba5e-645b-4bd9-89e0-1185ef22acb9",
                }
            ]
        )
        self.home.save_revision().publish()

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing data.")
        self.cleanup_existing_data()

        self.stdout.write("Starting to build fixtures.")
        self.create_locale()

        self.create_home_pages()
        self.create_content_pages()

        self.stdout.write("Done building fixtures.")
