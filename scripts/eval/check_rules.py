"""
Deterministic rule checks on collected candidate translations.
No LLM calls. Reads candidates_all.json, writes per-segment pass/fail + summary.

Checks per (segment, model):
  1. html_tags   - same tag set + same id attrs + same order as source
  2. bold_keep   - <b>/<i> text kept verbatim English (matches source text)
  3. bold_no_wrap- <b>/<i> text NOT wrapped in guillemets («»)
  4. no_trunc    - output length not suspiciously short vs source (truncation)
  5. no_bleed    - no reasoning/commentary bleed (no "Let me", "```", etc.)
  6. no_error    - translate_text returned no error

Usage:
    docker compose exec -T web python manage.py shell -c \
        "exec(open('scripts/eval/check_rules.py').read())"
"""

import json
import os
import re
from collections import defaultdict

from bs4 import BeautifulSoup

LANG_SLUG = os.environ.get("EVAL_LANG_SLUG", "arabic")

IN_PATH = f"/app/scripts/eval/out/{LANG_SLUG}/candidates/candidates_all.json"
OUT_DIR = f"/app/scripts/eval/out/{LANG_SLUG}/rules"

# Arabic reasoning-bleed markers (English + likely leakage prefixes).
BLEED_PATTERNS = [
    r"^```",
    r"^(sure|here is|let me|certainly|of course|translate|translation)\b",
    r"(here is the translation|let me translate|the translation is|note: |step \d)",
]
BLEED_RE = re.compile("|".join(BLEED_PATTERNS), re.IGNORECASE)

# Ratio threshold: Arabic output chars should be at least 0.3 * source chars.
# Source is English+HTML; Arabic is typically more verbose char-wise than English
# but if a model truncates the ratio collapses. Below 0.25 = suspicious truncation.
TRUNC_MIN_RATIO = 0.25

GUILLEMET_CHARS = "«»“”"


def _parse_tags(html: str):
    """Return list of (tag, id_attr) in order, plus set of tag names."""
    if not html:
        return [], set()
    soup = BeautifulSoup(html, "html.parser")
    tags = []
    for t in soup.find_all(True):
        tags.append((t.name, t.get("id")))
    return tags, {t[0] for t in tags}


def _bold_texts(html: str):
    """Return list of text content inside <b>/<i> tags (stripped)."""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    return [t.get_text().strip() for t in soup.find_all(["b", "i"])]


def check_one(source: str, candidate: str, error):
    """Return dict of rule->bool (True=pass, None=N/A)."""
    s_tags, s_tagset = _parse_tags(source)
    c_tags, c_tagset = _parse_tags(candidate)
    out = {}

    # 1. html_tags: same tag sequence + ids
    if s_tags:
        out["html_tags"] = s_tags == c_tags
    else:
        out["html_tags"] = None  # N/A (no tags in source)

    # 2. bold_keep: <b>/<i> text in source == text in candidate (verbatim)
    s_bold = _bold_texts(source)
    c_bold = _bold_texts(candidate)
    if s_bold:
        out["bold_keep"] = s_bold == c_bold
    else:
        out["bold_keep"] = None

    # 3. bold_no_wrap: guillemets do not appear inside or directly around <b>/<i>
    if c_bold:
        # heuristic: if any char from guillemets appears inside a bold tag's text
        wrapped = any(any(ch in GUILLEMET_CHARS for ch in bt) for bt in c_bold)
        out["bold_no_wrap"] = not wrapped
    else:
        out["bold_no_wrap"] = None

    # 4. no_trunc: candidate length ratio vs source
    s_len = len(source or "")
    c_len = len(candidate or "")
    if s_len > 0:
        out["no_trunc"] = (c_len / s_len) >= TRUNC_MIN_RATIO
    else:
        out["no_trunc"] = None

    # 5. no_bleed: candidate doesn't start with reasoning leakage
    if candidate:
        out["no_bleed"] = not BLEED_RE.search(candidate[:200])
    else:
        out["no_bleed"] = False

    # 6. no_error
    out["no_error"] = error is None

    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(IN_PATH, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["rows"]
    models = data["models"]

    # Per-row results
    results = []
    for r in rows:
        checks = check_one(
            r.get("source_text", ""),
            r.get("translated_text", ""),
            r.get("error"),
        )
        results.append(
            {
                "page_id": r["page_id"],
                "page_title": r["page_title"],
                "string_id": r["string_id"],
                "context_path": r["context_path"],
                "model": r["model"],
                "checks": checks,
            }
        )

    # Per-model aggregate: pass% over each rule (N/A excluded)
    agg = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "total": 0}))
    for r in results:
        m = r["model"]
        for rule, v in r["checks"].items():
            if v is None:
                continue
            agg[m][rule]["total"] += 1
            if v:
                agg[m][rule]["pass"] += 1

    # Print + write summary
    print("=" * 80)
    print("RULE-CHECK SUMMARY (pass% per rule per model; N/A segments excluded)")
    print("=" * 80)
    rules_order = [
        "no_error",
        "no_bleed",
        "html_tags",
        "bold_keep",
        "bold_no_wrap",
        "no_trunc",
    ]
    header = f"{'model':30s} " + " ".join(f"{r:>12s}" for r in rules_order)
    print(header)
    summary_csv_rows = []
    for m in models:
        parts = [f"{m:30s}"]
        for rule in rules_order:
            a = agg[m][rule]
            pct = (100.0 * a["pass"] / a["total"]) if a["total"] else float("nan")
            parts.append(f"{pct:>11.1f}%" if a["total"] else f"{'N/A':>12s}")
            summary_csv_rows.append(
                {
                    "model": m,
                    "rule": rule,
                    "pass": a["pass"],
                    "total": a["total"],
                    "pass_pct": round(pct, 1) if a["total"] else "N/A",
                }
            )
        print(" ".join(parts))

    # Write detailed per-segment results JSON
    detail_path = os.path.join(OUT_DIR, "rules_detail.json")
    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(
            {"models": models, "results": results}, f, ensure_ascii=False, indent=2
        )

    # Write summary CSV
    import csv

    summary_path = os.path.join(OUT_DIR, "rules_summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["model", "rule", "pass", "total", "pass_pct"])
        w.writeheader()
        w.writerows(summary_csv_rows)

    print("\nDetail JSON:", detail_path)
    print("Summary CSV:", summary_path)

    # List failures for quick inspection
    print("\n" + "=" * 80)
    print("FAILURES (segment, model, rule):")
    for r in results:
        for rule, v in r["checks"].items():
            if v is False:
                print(
                    f"  page{r['page_id']} [{r['context_path'][:30]:30s}] "
                    f"{r['model'][:28]:28s}  FAIL: {rule}"
                )


main()
