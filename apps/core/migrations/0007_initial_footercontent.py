# Generated by Django 4.1.2 on 2022-10-27 10:39

from django.db import migrations


def create_initial_footer_content(apps, schema_editor):
    Locale = apps.get_model("wagtailcore", "Locale")
    FooterContent = apps.get_model("core", "FooterContent")
    FooterItem = apps.get_model("core", "FooterItem")
    en_latest = Locale.objects.get(language_code="en-latest")

    footer_content = FooterContent.objects.create(
        locale=en_latest,
        copyright_text=(
            '<p data-block-key="q66lz">'
            "Copyright and related rights waived via "
            '<a href="https://creativecommons.org/publicdomain/zero/1.0">CC0</a>.'
            "</p>"
        ),
    )

    items_data = [
        {
            "title": "About this guide",
            "description": "Learn why we structured our documents like this",
            "link": "https://wagtail.org",
            "icon": "info",
        },
        {
            "title": "Help improve this guide",
            "description": "Contribute to open source with no coding experience needed",
            "link": "https://wagtail.org",
            "icon": "help",
        },
        {
            "title": "Wagtail",
            "description": "Visit Wagtail.org for more resources and Wagtail news",
            "link": "https://wagtail.org",
            "icon": "wagtail",
        },
    ]

    for data in items_data:
        FooterItem.objects.create(
            locale=en_latest,
            parent_footer=footer_content,
            **data,
        )


def remove_footer_content(apps, schema_editor):
    FooterContent = apps.get_model("core", "FooterContent")
    FooterContent.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_footercontent_footeritem"),
    ]

    operations = [
        migrations.RunPython(create_initial_footer_content, remove_footer_content),
    ]