"""Shared glossary helpers for the Promptfoo translation eval.

Reads the Wagtail admin translation glossaries exported by
`just eval-glossary <lang>` (prompts/evals/translations-inspect_ai/glossary/<lang>.json),
and mirrors the UI label extraction in apps/core/translator.py.
"""

import json
import re
from functools import cache
from html import unescape
from pathlib import Path

GLOSSARY_DIR = Path(__file__).parents[1] / "translations-inspect_ai" / "glossary"

UI_LABEL_RE = re.compile(r"<(b|i)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)


def ui_terms(html):
    """Unique <b>/<i> label texts, in order — as in LLMTranslator."""
    terms = []
    for _tag, text in UI_LABEL_RE.findall(html or ""):
        term = unescape(re.sub(r"<[^>]+>", "", text)).strip()
        if term and term not in terms:
            terms.append(term)
    return terms


@cache
def load_glossary(lang_code):
    path = GLOSSARY_DIR / f"{lang_code}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No glossary at {path} — generate it with: just eval-glossary {lang_code}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def matched_glossary(text, lang_code):
    """Official admin translations for the UI labels present in `text`."""
    glossary = load_glossary(lang_code)
    return {term: glossary[term] for term in ui_terms(text) if term in glossary}
