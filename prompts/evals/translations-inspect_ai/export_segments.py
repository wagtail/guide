"""
Export real translatable segments in the shared eval dataset format.

Optional — a hand-picked prompts/evals/translations/segments.yaml (extracted
from real guide content) is checked in. Use this to regenerate it from actual
page content (the output is a JSON array, which is valid YAML):

    docker compose exec -T web python manage.py shell -c \
        "exec(open('prompts/evals/translations-inspect_ai/export_segments.py').read())" \
        > prompts/evals/translations/segments.yaml
"""

import json
import os

from wagtail.models import Locale, Page
from wagtail_localize.models import TranslationSource

PAGE_IDS = [int(p) for p in os.environ.get("EVAL_PAGE_IDS", "10,66").split(",")]

cases = []
en = Locale.objects.get(language_code="en")
for pid in PAGE_IDS:
    page = Page.objects.filter(id=pid, locale=en).first() or (
        Page.objects.filter(
            translation_key=Page.objects.get(id=pid).translation_key, locale=en
        ).first()
    )
    if not page:
        continue
    source = TranslationSource.objects.filter(
        object_id=page.translation_key, locale=en
    ).first()
    if not source:
        continue
    for seg in source.stringsegment_set.select_related("string", "context").order_by(
        "order"
    ):
        cases.append(
            {
                "description": f"{page.title} — {seg.context.path if seg.context_id else 'segment'}",
                "metadata": {
                    "id": f"page{page.id}-{seg.string_id}",
                    "source": f"page {page.id}: {page.title}",
                },
                "vars": {"text": seg.string.as_value().get_translatable_html()},
            }
        )

print(json.dumps(cases, indent=2, ensure_ascii=False))
