# Generated for adding a non-determinable token to Feedback.

import uuid

from django.db import migrations, models


def populate_tokens(apps, schema_editor):
    Feedback = apps.get_model("core", "Feedback")
    for feedback in Feedback.objects.all():
        feedback.token = uuid.uuid4()
        feedback.save(update_fields=["token"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_remove_contentpage_table_of_contents"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="token",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.RunPython(populate_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="feedback",
            name="token",
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
