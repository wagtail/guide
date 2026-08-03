"""
Cost review for an already-translated page, straight from the saved
wagtail_localize_ai.TranslationLog rows. NO LLM calls, free and instant.

The log rows are created when you click "Translate with AI" in the Wagtail
admin. One aggregated row is written per page run (provider, model, total
input/output tokens), so this script reports PER-PAGE cost — not per string.

Usage:
    docker compose exec -T web python manage.py shell -c \
        "exec(open('scripts/page_cost.py').read())"

Before running:
- Set PAGE_ID (or PAGE_TITLE_SUBSTRING) to the page that was translated.
- Set TARGET_LANG_CODE to the locale it was translated to.
- Set PRICING to the model's per-1M-token rates. (None, None) -> "?" in $.
"""
import csv
import os
import re
from datetime import timedelta

from django.utils import timezone
from django.utils.translation import get_language_info
from wagtail.models import Page, Locale
from wagtail_localize.models import TranslationSource, Translation, StringTranslation

from wagtail_localize_ai.models import TranslationLog

# === Config (edit these) ===
# Pick the page by id OR by title substring (case-insensitive). If both are set,
# PAGE_ID wins. Leave PAGE_ID=None and set PAGE_TITLE_SUBSTRING to match by name.
PAGE_ID = 66
# PAGE_TITLE_SUBSTRING = "manage documents"   # resolves Arabic aliases to English source automatically
TARGET_LANG_CODE = "ar"   # target locale language_code

# Log rows are matched to this page's translation run by timestamp. The admin
# run fires within seconds of Translation creation; widen this only if the page
# was slow to translate (long pages can take minutes).
LOG_WINDOW_MINUTES = 5

PRICING = {
    # {model_name: (input_per_1M, output_per_1M, currency_symbol)}.
    # Fill from each provider's pricing page. (None, None) -> cost column shows "?".
    "z-ai/glm-5.2": (1.40, 4.40, "$"),
    "google/gemma-4-26b-a4b-it":(0.07,0.34, "$"),
    "deepseek/deepseek-v4-flash": (0.14, 0.28, "$"),
    "MiniMax-M2.7": (0.60, 3.00, "£"),
    "DeepSeek-V3.2": (None, None, "£"),
    "gemma-4-31B-it": (0.60, 3.00, "£"),
}
DEFAULT_CURRENCY = "$"


def _slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", s or "").strip("-") or "model"


def _compute_cost(model_name, in_tok, out_tok):
    rates = PRICING.get(model_name)
    if not rates or rates[0] is None or rates[1] is None:
        return None, DEFAULT_CURRENCY
    in_rate, out_rate, cur = rates
    return (in_tok / 1_000_000 * in_rate) + (out_tok / 1_000_000 * out_rate), cur


def _fmt_cost(cost, cur):
    if cost is None:
        return "?"
    return f"{cur}{cost:.6f}"


def main():
    # 1. Resolve the page. Arabic alias auto-resolves to English source, since
    # TranslationSource rows are created from-English only.
    try:
        en_locale = Locale.objects.get(language_code="en")
    except Locale.DoesNotExist:
        print("No 'en' locale found in DB.")
        return

    if PAGE_ID:
        picked = Page.objects.get(id=PAGE_ID)
    elif PAGE_TITLE_SUBSTRING:
        matches = list(
            Page.objects.filter(title__icontains=PAGE_TITLE_SUBSTRING).order_by("id")
        )
        if not matches:
            print(f"No page found with title containing {PAGE_TITLE_SUBSTRING!r}.")
            return
        if len(matches) > 1:
            print(f"Multiple pages match {PAGE_TITLE_SUBSTRING!r}:")
            for p in matches:
                print(f"  id={p.id}  {p.title}")
            print("Set PAGE_ID to one of these ids in scripts/page_cost.py to disambiguate.")
            return
        picked = matches[0]
    else:
        print("Set PAGE_ID or PAGE_TITLE_SUBSTRING in scripts/page_cost.py.")
        return

    if picked.locale_id != en_locale.id:
        page = Page.objects.filter(
            translation_key=picked.translation_key, locale=en_locale
        ).first()
        if not page:
            print(
                f"Page {picked.title!r} (id={picked.id}, locale="
                f"{picked.locale.language_code!r}) has no English source sibling."
            )
            return
    else:
        page = picked

    source_locale = page.locale
    try:
        target_locale = Locale.objects.get(language_code=TARGET_LANG_CODE)
    except Locale.DoesNotExist:
        print(f"No locale with language_code={TARGET_LANG_CODE!r}.")
        return

    try:
        source = TranslationSource.objects.get(
            object_id=page.translation_key, locale=source_locale
        )
    except TranslationSource.DoesNotExist:
        print(f"No TranslationSource for page {page.title!r} (id={page.id}).")
        print("Has this page ever been submitted for translation?")
        return

    # 2. Anchor the log window on when this page's translations were last
    # written by the AI run. Translation.created_at is the *original* submit
    # date and goes stale when "Translate with AI" is re-run later. The
    # StringTranslation rows for this page+locale are updated at the moment the
    # run saves its output, which coincides with the log row timestamp.
    page_string_ids = list(source.stringsegment_set.values_list("string_id", flat=True))
    page_context_ids = list(source.stringsegment_set.values_list("context_id", flat=True))
    saved = StringTranslation.objects.filter(
        translation_of_id__in=page_string_ids,
        context_id__in=page_context_ids,
        locale=target_locale,
    )
    saved_machine = saved.filter(translation_type=StringTranslation.TRANSLATION_TYPE_MACHINE)

    latest_save = saved_machine.order_by("-updated_at").values_list("updated_at", flat=True).first()

    try:
        translation = Translation.objects.get(source=source, target_locale=target_locale)
    except Translation.DoesNotExist:
        print(f"No Translation row for {page.title!r} -> {TARGET_LANG_CODE!r}.")
        print("Has this page ever been translated to that locale via the admin?")
        return

    # Prefer the AI-save timestamp; fall back to the Translation creation time.
    anchor = latest_save or translation.created_at
    if not anchor:
        print(f"No TranslationLog-relevant timestamp found for {page.title!r}.")
        return

    window_start = anchor - timedelta(minutes=LOG_WINDOW_MINUTES)
    window_end = anchor + timedelta(minutes=LOG_WINDOW_MINUTES)

    log_qs = TranslationLog.objects.filter(
        timestamp__gte=window_start,
        timestamp__lte=window_end,
    ).order_by("timestamp")

    logs = list(log_qs)

    if not logs:
        print(f"No TranslationLog rows found within ±{LOG_WINDOW_MINUTES}min of "
              f"the latest translation save ({anchor:%H:%M:%S}).")
        print("Widen LOG_WINDOW_MINUTES, or check that AI translation was used.")
        return

    # 3. Sum tokens across all log rows belonging to this page's run.
    total_in = sum(l.input_tokens for l in logs)
    total_out = sum(l.output_tokens for l in logs)
    matched_model = logs[-1].model
    matched_provider = logs[-1].provider
    errors = [l.error for l in logs if l.error]

    # 4. Compute $ from tokens × rates.
    cost, cur = _compute_cost(matched_model, total_in, total_out)
    total_segments = source.stringsegment_set.count()
    n = total_segments or 1

    source_language = get_language_info(source_locale.language_code)["name"]
    target_language = get_language_info(target_locale.language_code)["name"]

    print("=" * 80)
    print(f"Page: {page.title!r} (id={page.id})")
    print(f"Source locale: {source_language} ({source_locale.language_code})")
    print(f"Target locale: {target_language} ({target_locale.language_code})")
    print(f"Provider: {matched_provider or '?'}   Model: {matched_model or '?'}")
    print(f"Segments on page: {total_segments}   Matched log rows: {len(logs)}")
    print(f"Log timespan: {logs[0].timestamp:%Y-%m-%d %H:%M:%S} -> {logs[-1].timestamp:%Y-%m-%d %H:%M:%S}")
    print(f"Data source: saved TranslationLog (read-only, no LLM calls)")
    print("=" * 80)
    print("=" * 80)
    print(f"PAGE COST:  page={page.title!r} (id={page.id})  model={matched_model or '?'}")
    print(f"            segments={total_segments}   input_tokens={total_in}   output_tokens={total_out}   total_tokens={total_in + total_out}")
    if cost is not None:
        print(f"            >>> PAGE COST = {_fmt_cost(cost, cur)} <<<")
        print(f"            avg per string = {_fmt_cost(cost / n, cur)}")
    else:
        print(f"            (rates missing for model {matched_model!r} in PRICING; fill PRICING to compute $).")
    if errors:
        print(f"NOTE: {len(errors)} log row(s) had errors during translation.")
    print("=" * 80)

    csv_dir = "/app/scripts/eval"  # container path; mounts to repo scripts/eval
    csv_path = os.path.join(
        csv_dir,
        f"cost_page{page.id}_{_slugify(matched_model)}.csv",
    )
    os.makedirs(csv_dir, exist_ok=True)
    fieldnames = [
        "page_id",
        "page_title",
        "provider",
        "model",
        "log_rows",
        "segments",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "cost",
        "currency",
        "run_start",
        "run_end",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "page_id": page.id,
                "page_title": page.title,
                "provider": matched_provider,
                "model": matched_model,
                "log_rows": len(logs),
                "segments": total_segments,
                "input_tokens": total_in,
                "output_tokens": total_out,
                "total_tokens": total_in + total_out,
                "cost": "" if cost is None else f"{cost:.6f}",
                "currency": cur,
                "run_start": logs[0].timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "run_end": logs[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    print(f"\nCSV written to: {csv_path}")


main()
