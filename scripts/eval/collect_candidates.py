"""
Pilot eval: translate a SMALL sample of source segments through each candidate
model using the real fork translate_text (same SYSTEM_PROMPT, sanitize_html,
StringValue validation as the admin button). No DB writes — outputs go to JSON.

Usage:
    docker compose exec -T web python manage.py shell -c \
        "exec(open('scripts/eval/collect_candidates.py').read())"

Output:
    /app/scripts/eval/out/candidates/<page_id>_<model_slug>.json
    /app/scripts/eval/out/candidates/candidates_all.json
"""

import concurrent.futures
import json
import logging
import os
import re
import warnings

logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

from wagtail.models import Locale, Page
from wagtail_localize.models import TranslationSource
from wagtail_localize_ai.models import AITranslatorSettings
from wagtail_localize_ai.translator import translate_text

# === Config ===
PAGE_IDS = [10, 66]  # Concepts (4) + Manage documents (11) = 15 segs
CANDIDATE_MODELS = [
    "z-ai/glm-5.2",
    "deepseek/deepseek-v4-flash",
    "google/gemma-4-26b-a4b-it",
]
PROVIDER = "kilo"
MAX_WORKERS = 3
SOURCE_LANGUAGE = "English"

# Target language for this run. Switch this to evaluate a different locale.
TARGET_LANGUAGE = os.environ.get("EVAL_TARGET_LANGUAGE", "Arabic")
LANG_SLUG = os.environ.get("EVAL_LANG_SLUG", TARGET_LANGUAGE.lower())

OUT_DIR = f"/app/scripts/eval/out/{LANG_SLUG}/candidates"


def _slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", s or "").strip("-") or "model"


def _gather_segments():
    """Return list of dicts: page_id, page_title, string_id, context_path, source."""
    en = Locale.objects.get(language_code="en")
    segments = []
    for pid in PAGE_IDS:
        try:
            page = Page.objects.get(id=pid)
        except Page.DoesNotExist:
            print(f"  page id={pid} not found, skipping")
            continue
        if page.locale_id != en.id:
            page = Page.objects.filter(
                translation_key=page.translation_key, locale=en
            ).first()
            if not page:
                print(f"  page id={pid} has no English source, skipping")
                continue
        try:
            source = TranslationSource.objects.get(
                object_id=page.translation_key, locale=en
            )
        except TranslationSource.DoesNotExist:
            print(
                f"  page id={pid} ({page.title!r}) has no TranslationSource, skipping"
            )
            continue
        for seg in source.stringsegment_set.select_related(
            "string", "context"
        ).order_by("order"):
            segments.append(
                {
                    "page_id": page.id,
                    "page_title": page.title,
                    "string_id": seg.string_id,
                    "context_path": seg.context.path if seg.context_id else "",
                    "source_text": seg.string.as_value().get_translatable_html(),
                    "_sv": seg.string.as_value(),
                }
            )
    return segments


def _translate_one(seg, model, _orig_load):
    """Worker: patch settings to model, translate one segment, restore semantics."""

    def _patched_load():
        s = _orig_load()
        s.model = model
        s.provider = PROVIDER
        return s

    AITranslatorSettings.load = staticmethod(_patched_load)
    try:
        result = translate_text(seg["_sv"], SOURCE_LANGUAGE, TARGET_LANGUAGE)
    except Exception as e:  # noqa: BLE001 - collect any model/provider failure
        result = {"error": str(e)}
    usage = result.get("usage") or {"input_tokens": 0, "output_tokens": 0}

    # Fork-main success path returns {"result": {StringValue: StringValue}, "usage": ...}
    # The PR#1 path also had "translated_text"/"source_text". Handle both.
    translated_text = result.get("translated_text") or ""
    if not translated_text and "result" in result:
        res_map = result["result"] or {}
        if res_map:
            sv_out = next(iter(res_map.values()))
            translated_text = sv_out.get_translatable_html() if sv_out else ""

    return {
        "page_id": seg["page_id"],
        "page_title": seg["page_title"],
        "string_id": seg["string_id"],
        "context_path": seg["context_path"],
        "model": model,
        "source_text": result.get("source_text") or seg["source_text"],
        "translated_text": translated_text,
        "error": result.get("error") or None,
        "input_tokens": usage.get("input_tokens", 0) or 0,
        "output_tokens": usage.get("output_tokens", 0) or 0,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    _orig_load = AITranslatorSettings.load
    segments = _gather_segments()
    print(f"Sample: {len(segments)} segments across {len(PAGE_IDS)} pages")
    print(f"Candidate models: {CANDIDATE_MODELS}")
    print(f"Total translation calls: {len(segments) * len(CANDIDATE_MODELS)}")
    print("=" * 70)

    all_rows = []
    totals = {m: {"in": 0, "out": 0, "errors": 0} for m in CANDIDATE_MODELS}

    for model in CANDIDATE_MODELS:
        print(f"\n>>> Translating with {model} ...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            rows = list(
                ex.map(lambda seg: _translate_one(seg, model, _orig_load), segments)
            )
        # Restore
        AITranslatorSettings.load = _orig_load

        for r in rows:
            totals[model]["in"] += r["input_tokens"]
            totals[model]["out"] += r["output_tokens"]
            if r["error"]:
                totals[model]["errors"] += 1
        all_rows.extend(rows)

        # Write per-page grouping for this model
        by_page = {}
        for r in rows:
            by_page.setdefault(r["page_id"], []).append(r)
        for pid, prows in by_page.items():
            path = os.path.join(OUT_DIR, f"page{pid}_{_slugify(model)}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "page_id": pid,
                        "page_title": prows[0]["page_title"],
                        "model": model,
                        "segments": prows,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        print(
            f"    done: {len(rows)} segs, "
            f"in={totals[model]['in']} out={totals[model]['out']} "
            f"errors={totals[model]['errors']}"
        )

    all_path = os.path.join(OUT_DIR, "candidates_all.json")
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(
            {"models": CANDIDATE_MODELS, "segments": len(segments), "rows": all_rows},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\n" + "=" * 70)
    print("SUMMARY (per model):")
    for m, t in totals.items():
        total = t["in"] + t["out"]
        print(
            f"  {m:35s}  in={t['in']:6d} out={t['out']:6d} total={total:6d} errors={t['errors']}"
        )
    print(f"\nCandidates JSON: {all_path}")
    print(f"Per-page files in: {OUT_DIR}/page<id>_<model>.json")


main()
