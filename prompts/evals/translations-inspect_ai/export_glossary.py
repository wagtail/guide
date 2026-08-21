"""
Export merged Django/Wagtail translation catalogs as glossary JSON files.

The output is the same catalog `apps/core/translator.py` reads live via
Django's translation machinery — this build step just makes it available to
the Inspect eval, which runs outside the project environment.

Usage (from the project root, one file per language code):

    uv run python prompts/evals/translations-inspect_ai/export_glossary.py ar is fr
    # or: just eval-glossary ar is fr

Output: prompts/evals/translations-inspect_ai/glossary/<lang>.json  ({"Collection": "Safn", ...})
"""

import json
import os
import sys
from pathlib import Path

# Make the project root importable when run by path.
sys.path.insert(0, str(Path(__file__).parents[3]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.guide.settings.test")

import django

django.setup()

from django.utils.translation import trans_real

OUT_DIR = Path(__file__).parent / "glossary"
OUT_DIR.mkdir(exist_ok=True)

for lang in sys.argv[1:] or ["ar"]:
    catalog = trans_real.translation(lang)._catalog
    entries = {}
    for key in catalog.keys():
        # Skip plural entries (tuple keys) and contextual entries (ctx\x04msgid).
        if not isinstance(key, str) or "\x04" in key:
            continue
        value = catalog.get(key)
        if isinstance(value, str) and value.strip():
            entries[key] = value
    path = OUT_DIR / f"{lang}.json"
    path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{path}: {len(entries)} entries")
