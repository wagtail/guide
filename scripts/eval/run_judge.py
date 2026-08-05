"""
LLM-as-judge: GPT-5.1 scores candidate translations pairwise (all 3 candidates
in one call per segment, randomly labelled A/B/C to avoid position bias).
Reference-free: judge sees source + candidates, returns JSON ranks + scores.

Usage:
    docker compose exec -T web python manage.py shell -c \
        "exec(open('scripts/eval/run_judge.py').read())"

Set SMOKE_TEST=1 in the script to run only the first segment (cheap validation
of model id + response shape before the full run).

Output:
    /app/scripts/eval/out/judge/judge_results.json
"""

import json
import logging
import os
import random
import warnings

logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

from wagtail_localize_ai.utils import get_llm_client

# === Config ===
CANDIDATES_PATH = "/app/scripts/eval/out/candidates/candidates_all.json"
OUT_PATH = "/app/scripts/eval/out/judge/judge_results.json"

# Target language for this run.
TARGET_LANGUAGE = os.environ.get("EVAL_TARGET_LANGUAGE", "Arabic")
LANG_SLUG = os.environ.get("EVAL_LANG_SLUG", TARGET_LANGUAGE.lower())
CANDIDATES_PATH = f"/app/scripts/eval/out/{LANG_SLUG}/candidates/candidates_all.json"
OUT_PATH = f"/app/scripts/eval/out/{LANG_SLUG}/judge/judge_results.json"

JUDGE_PROVIDER = "kilo"
JUDGE_MODEL = "anthropic/claude-sonnet-5"  # confirm via smoke test
JUDGE_TEMPERATURE = 0

# Smoke test: judge only the first segment. Cheap (one call) validation of the
# model id and response shape. Set False for the full run.
SMOKE_TEST = False

random.seed(42)  # stable shuffle for reproducibility


JUDGE_SYSTEM = f"""You are an expert reviewer of {TARGET_LANGUAGE} machine translation quality for a software user guide.

You will receive:
- SOURCE: the English source text (may contain HTML tags like <a id="..">, <b>, <i>).
- Three candidate {TARGET_LANGUAGE} translations labelled A, B, C (random order). Each preserves the same HTML where possible.

Rules the translation MUST follow (the translator's system prompt):
1. HTML tags and their id attributes must match the source exactly — same tags, same order, no added attributes.
2. Text inside <b> or <i> tags is a UI label/button (e.g. <b>Documents</b>); it MUST stay in English verbatim and NOT be wrapped in guillemets «». Do NOT translate <b>/<i> content.
3. Other UI/product names in <b>/<i> also stay English. Plain prose and link text (NOT inside <b>/<i>) SHOULD be translated to {TARGET_LANGUAGE}.
4. No reasoning, commentary, or markdown fences in the output — only the translated text.
5. Translation must be complete (no truncation) and grammatically fluent formal {TARGET_LANGUAGE}.
6. Use one consistent term per concept.

Score each candidate on three 0-5 integer scales:
- accuracy: meaning preserved, no omissions/additions, no mistranslations
- fluency: natural, grammatical, formal {TARGET_LANGUAGE}
- rules: compliance with the rules above (HTML / <b> English / no truncation / no bleed)

Then give a rank: 1 = best, 3 = worst. Ties allowed (e.g. two candidates can both be rank 1).

Return ONLY a JSON object, no prose, exactly this shape:
{{
  "A": {{"accuracy": int, "fluency": int, "rules": int, "notes": "short reason in English"}},
  "B": {{"accuracy": int, "fluency": int, "rules": int, "notes": "..."}},
  "C": {{"accuracy": int, "fluency": int, "rules": int, "notes": "..."}}
}}
"""


def _judge_one(source, candidates_map):
    """candidates_map: {label: text} for labels A/B/C. Returns parsed JSON dict."""
    client = get_llm_client(JUDGE_PROVIDER)

    user = f"SOURCE:\n{source}\n\n"
    for label in ("A", "B", "C"):
        user += f"\nCandidate {label}:\n{candidates_map[label]}\n"
    user += "\nReturn ONLY the JSON object."

    messages = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user},
    ]

    response = client.completion(
        model=JUDGE_MODEL,
        temperature=JUDGE_TEMPERATURE,
        messages=messages,
    )
    content = (response.choices[0].message.content or "").strip()
    # Strip any accidental code fences
    if content.startswith("```"):
        content = content.split("```")
        # find the chunk that looks like JSON
        content = next(
            (c for c in content if c.strip().startswith("{")),
            content[-1] if content else "",
        )
    content = content.strip().strip("`")
    try:
        return json.loads(content), None
    except Exception as e:  # noqa: BLE001 - judge may return non-JSON
        return None, f"parse failed: {e}; raw[:200]={content[:200]!r}"


def main():
    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["rows"]
    models = data["models"]

    # Group rows by (page_id, string_id, context_path, source_text) -> {model: translated}
    groups = {}
    for r in rows:
        key = (r["page_id"], r["string_id"], r["context_path"], r["source_text"])
        groups.setdefault(key, {})[r["model"]] = r["translated_text"]

    seg_list = list(groups.items())
    if SMOKE_TEST:
        seg_list = seg_list[:1]
        print(f"SMOKE TEST: judging 1 segment with {JUDGE_MODEL} via {JUDGE_PROVIDER}")
    else:
        print(
            f"Judging {len(seg_list)} segments with {JUDGE_MODEL} via {JUDGE_PROVIDER}"
        )

    results = []
    for i, (key, model_outputs) in enumerate(seg_list, start=1):
        page_id, string_id, context_path, source_text = key
        # Shuffle labels per segment to avoid position bias
        assigned = list(models)
        random.shuffle(assigned)
        labels = ["A", "B", "C"][: len(assigned)]
        candidates_map = {
            lab: (model_outputs[m] or "") for lab, m in zip(labels, assigned)
        }
        label_to_model = dict(zip(labels, assigned))

        judgement, err = _judge_one(source_text, candidates_map)
        results.append(
            {
                "page_id": page_id,
                "string_id": string_id,
                "context_path": context_path,
                "source_text": source_text,
                "label_to_model": label_to_model,
                "candidates": candidates_map,
                "judgement": judgement,
                "error": err,
            }
        )
        if err:
            print(
                f"  seg {i}/{len(seg_list)} page{page_id} [{context_path[:25]}] ERROR: {err}"
            )
        else:
            j = judgement or {}
            scores = " ".join(
                f"{lab}:acc={j[lab]['accuracy']}/flu={j[lab]['fluency']}/rules={j[lab]['rules']}"
                for lab in labels
                if lab in j
            )
            print(
                f"  seg {i}/{len(seg_list)} page{page_id} [{context_path[:25]}] {scores}"
            )

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"judge_model": JUDGE_MODEL, "results": results},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nResults: {OUT_PATH}")


main()
