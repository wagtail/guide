#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["inspect-ai", "openai", "pyyaml"]
# ///
"""
Document-level (whole-page) translation eval with Inspect AI.

Like translation_task.py, but each sample is an ENTIRE page: all segments of
a page are translated in ONE LLM request, wrapped in an XML envelope
(<document> with <segment id="..."> children). Concatenating the segments is
what makes whole-page terminology consistency gradeable — the judge sees one
document, so "one term per concept throughout the page" is a real criterion,
not a per-segment approximation.

Dataset: prompts/evals/translations-batch/documents.json, generated from real
guide content by build_documents.py. The candidate replies with the same
envelope; rule checks and the LLM judge decode it segment-by-segment.

Candidate and judge models are declared in CANDIDATE_MODELS / JUDGE_MODEL.
Credentials come from the standard Scaleway environment variables
(SCW_SECRET_KEY, SCW_DEFAULT_PROJECT_ID), e.g. via the project `.env`.

Run it directly (uv resolves the inline dependencies):

    ./prompts/evals/translations-inspect_ai/translation_batch_task.py
    ./prompts/evals/translations-inspect_ai/translation_batch_task.py --limit 1 --target-language Icelandic --lang-code is

or via just:

    just eval-translations-batch
    just eval-view
"""

import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import (
    ChatMessageAssistant,
    ChatMessageSystem,
    ChatMessageUser,
    GenerateConfig,
)
from inspect_ai.scorer import Score, Target, accuracy, model_graded_qa, scorer, stderr
from inspect_ai.solver import TaskState, generate, solver

# Scaleway Generative APIs (OpenAI Chat Completions compatible), accessed
# through Inspect's `openai-api/<provider>/<model>` naming.
CANDIDATE_MODELS = [
    "openai-api/scaleway/deepseek-v4-flash-0731",
    "openai-api/scaleway/mistral-medium-3.5-128b",
    "openai-api/scaleway/gemma-4-26b-a4b-it",
]
JUDGE_MODEL = "openai-api/scaleway/glm-5.2"

LOG_DIR = str(Path(__file__).parent / "logs")
GLOSSARY_DIR = Path(__file__).parent / "glossary"
# Whole-page segment lists, generated from real guide content by
# prompts/evals/translations-batch/build_documents.py.
DOCUMENTS_PATH = Path(__file__).parents[1] / "translations-batch" / "documents.json"

try:
    # Single source of truth when run inside the project environment.
    from apps.core.translator import LLMTranslator

    SYSTEM_PROMPT = str(LLMTranslator.default_system_prompt)
    GLOSSARY_PROMPT = str(LLMTranslator.default_glossary_prompt)
except Exception:  # noqa: BLE001 - any Django/Wagtail setup failure
    # Fallback copies for running outside Django. Keep in sync with
    # apps/core/translator.py.
    SYSTEM_PROMPT = (
        "You are a professional translator translating text from "
        "{source_language} to {target_language}.\n"
        "Translate only the text and keep its structure intact.\n"
        "Reply with just the translated text and no wrapper, explanation, or "
        "code fence of any kind.\n"
        "- Only standard HTML inline tags are allowed: a, abbr, acronym, b, "
        "code, em, i, strong, br.\n"
        "- <a> tags may keep only their id attribute; other tags must have no "
        "attributes.\n"
        "- Preserve any inline tags, whitespace, and punctuation exactly."
    )
    GLOSSARY_PROMPT = (
        "\n- Text inside <b> or <i> tags is usually a label from the Wagtail "
        "admin interface. When a term appears in the glossary below, use the "
        "official translation exactly as given; otherwise translate it "
        "naturally and consistently.\n"
        "Glossary (official Wagtail admin translations):\n{glossary}"
    )

# Whole-document format instructions, from the batch eval's prompt module.
FORMAT_INSTRUCTIONS = (
    "The document is a list of segments wrapped in XML. Translate it as "
    "ONE document and reply with the same XML structure, with the same "
    "segment ids in the same order:\n"
    "<document>\n"
    '<segment id="s1">translated text</segment>\n'
    '<segment id="s2">translated text</segment>\n'
    "</document>\n"
    "Reply with the <document> XML and nothing else - no wrapper, "
    "explanation, or code fence of any kind. Translate every segment; "
    "never drop, merge, reorder, add, or repeat segments."
)

# Few-shot example: generic English/French so it works for every target
# language; demonstrates same ids, same order, tags preserved, slug segments
# kept as-is.
FEWSHOT_SOURCE = (
    "<document>\n"
    '<segment id="s1">Getting started</segment>\n'
    '<segment id="s2">getting-started</segment>\n'
    '<segment id="s3">Click <b>Save</b> in the <a id="a1">edit screen</a> '
    "to keep your work.</segment>\n"
    "</document>"
)
FEWSHOT_TARGET = (
    "<document>\n"
    '<segment id="s1">Premiers pas</segment>\n'
    '<segment id="s2">getting-started</segment>\n'
    '<segment id="s3">Cliquez sur <b>Enregistrer</b> dans l\''
    '<a id="a1">écran de modification</a> pour conserver votre '
    "travail.</segment>\n"
    "</document>"
)

UI_LABEL_RE = re.compile(r"<(b|i)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)


def ui_terms(html: str) -> list[str]:
    """Unique <b>/<i> label texts, in order — as in LLMTranslator."""
    terms = []
    for _tag, text in UI_LABEL_RE.findall(html or ""):
        term = _label_text(text)
        if term and term not in terms:
            terms.append(term)
    return terms


def _label_text(raw: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", raw)).strip()


def load_glossary(lang_code: str) -> dict[str, str]:
    path = GLOSSARY_DIR / f"{lang_code}.json"
    if not path.exists():
        print(
            f"WARNING: no glossary at {path} — UI label consistency will not "
            f"be prompted or scored. Generate it with: just eval-glossary {lang_code}"
        )
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_dataset() -> MemoryDataset:
    docs = json.loads(DOCUMENTS_PATH.read_text(encoding="utf-8"))
    return MemoryDataset(
        [
            Sample(
                id=f"{doc['id']}",
                input=render_document(json.loads(doc["vars"]["doc"])),
                metadata={
                    "description": doc["description"],
                    "doc_id": doc["id"],
                    "cases": doc["vars"]["doc"],
                },
            )
            for doc in docs
        ]
    )


def render_document(cases: list[dict]) -> str:
    """Concatenate segments into the XML envelope the candidate receives."""
    lines = ["<document>"]
    for case in cases:
        lines.append(f'<segment id="{case["id"]}">{case["text"]}</segment>')
    lines.append("</document>")
    return "\n".join(lines)


def parse_document(output: str) -> tuple[list[tuple[str, str]] | None, str | None]:
    """Decode the envelope into [(id, text)] in order, or (None, error)."""
    stripped = (output or "").strip()
    if not stripped:
        return None, "empty output"
    if not re.match(r"<\s*document\b", stripped):
        return None, "output does not start with <document>"
    segs = re.findall(
        r'<segment\s+id="([^"]+)"\s*>(.*?)</segment>', stripped, re.DOTALL
    )
    if not segs:
        return None, "no <segment> elements found in <document>"
    return segs, None


# --- Solver: per-sample system prompt with glossary, as in production --------


@solver
def translator_prompt(system_prompt: str, glossary: dict[str, str]):
    """Prepend the translator system prompt + whole-document glossary + format
    instructions, then the few-shot example and the document (mirrors the
    batch eval's prompt function; glossary spans the whole page)."""

    async def solve(state: TaskState, generate):
        cases = json.loads(state.metadata["cases"])
        doc_text = "\n".join(case["text"] for case in cases)
        matched = {
            term: glossary[term] for term in ui_terms(doc_text) if term in glossary
        }
        lines = "\n".join(f"- {src} = {dst}" for src, dst in matched.items())
        # Stash for the judge template ({glossary} via sample metadata).
        state.metadata["glossary"] = lines or "(none for this document)"
        prompt = system_prompt
        if matched:
            prompt += GLOSSARY_PROMPT.format(glossary=lines)
        prompt += "\n" + FORMAT_INSTRUCTIONS
        state.messages.insert(0, ChatMessageSystem(content=prompt))
        # Few-shot example as a user/assistant pair, as in the batch eval.
        state.messages.insert(1, ChatMessageUser(content=FEWSHOT_SOURCE))
        state.messages.insert(2, ChatMessageAssistant(content=FEWSHOT_TARGET))
        return state

    return solve


# --- Deterministic rule scorer (stdlib only, no bs4) -------------------------


class _TagCollector(HTMLParser):
    """Collects (tag, attrs) in document order and text inside <b>/<i>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.bold_texts = []
        self._bold_depth = 0
        self._bold_buf = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, tuple(sorted(attrs))))
        if tag in ("b", "i"):
            self._bold_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, tuple(sorted(attrs))))

    def handle_endtag(self, tag):
        if tag in ("b", "i") and self._bold_depth:
            self._bold_depth -= 1
            if not self._bold_depth:
                self.bold_texts.append("".join(self._bold_buf).strip())
                self._bold_buf = []

    def handle_data(self, data):
        if self._bold_depth:
            self._bold_buf.append(data)


def _parse(html: str) -> _TagCollector:
    collector = _TagCollector()
    collector.feed(html or "")
    collector.close()
    return collector


BLEED_RE = re.compile(
    r"^```|^(sure|here is|let me|certainly|of course|translation)\b"
    r"|(here is the translation|let me translate|the translation is)",
    re.IGNORECASE,
)
TRUNC_MIN_RATIO = 0.25


@scorer(metrics={"*": [accuracy(), stderr()]})
def rule_checks(glossary: dict[str, str]):
    """Format rules from the translator system prompt, checked mechanically
    per SEGMENT of the decoded envelope (whole document at a time).

    envelope   reply parses as <document> with the same ids in order
    tags       per segment: same tag sequence + attributes as the source
    glossary   per segment: <b>/<i> labels use the official Wagtail translation
    no_trunc   per segment: output not suspiciously short vs source
    no_bleed   no code fences or commentary preamble around the envelope

    Checks that don't apply (e.g. no glossary term in the document) score 1.
    """

    async def score(state: TaskState, target: Target) -> Score:
        candidate = (state.output.completion or "").strip()
        cases = json.loads(state.metadata["cases"])
        src = {case["id"]: case["text"] for case in cases}

        parsed, error = parse_document(candidate)
        if error:
            return Score(
                value={
                    "envelope": 0,
                    "tags": 0,
                    "glossary": 0,
                    "no_trunc": 0,
                    "no_bleed": 0,
                },
                answer=candidate,
                explanation=f"FAIL: {error}",
            )

        got_ids = [sid for sid, _text in parsed]
        envelope_ok = got_ids == list(src)

        tag_failures = []
        glossary_failures = []
        trunc_failures = []
        tags_ok = True
        glossary_ok = True
        trunc_ok = True
        for sid, text in parsed:
            if sid not in src:
                continue
            src_parsed = _parse(src[sid])
            cand_parsed = _parse(text)
            if src_parsed.tags != cand_parsed.tags:
                tags_ok = False
                tag_failures.append(sid)
            # Position-wise comparison of <b>/<i> labels against the glossary.
            expected = [
                (i, glossary[term])
                for i, term in enumerate(src_parsed.bold_texts)
                if term in glossary
            ]
            if expected:
                if len(cand_parsed.bold_texts) != len(src_parsed.bold_texts):
                    glossary_ok = False
                    glossary_failures.append(f"{sid}: <b>/<i> count differs")
                else:
                    for i, official in expected:
                        if cand_parsed.bold_texts[i] != official:
                            glossary_ok = False
                            glossary_failures.append(
                                f"{sid}: label should be {official!r}, "
                                f"got {cand_parsed.bold_texts[i]!r}"
                            )
            if len(text.strip()) < TRUNC_MIN_RATIO * len(src[sid]):
                trunc_ok = False
                trunc_failures.append(sid)

        bleed_ok = bool(candidate) and not BLEED_RE.search(candidate[:200])

        checks = {
            "envelope": envelope_ok,
            "tags": tags_ok,
            "glossary": glossary_ok,
            "no_trunc": trunc_ok,
            "no_bleed": bleed_ok,
        }
        failures = []
        if not envelope_ok:
            missing = [s for s in src if s not in got_ids]
            extra = [s for s in got_ids if s not in src]
            failures.append(
                f"envelope: missing={missing} extra={extra}"
                if missing or extra
                else "envelope: ids out of order"
            )
        if tag_failures:
            failures.append(f"tags differ in segments {tag_failures[:5]}")
        if glossary_failures:
            failures.append("; ".join(glossary_failures[:3]))
        if trunc_failures:
            failures.append(f"suspiciously short segment(s): {trunc_failures[:5]}")
        if not bleed_ok:
            failures.append("no_bleed: commentary or code fence detected")

        return Score(
            value={name: 1 if passed else 0 for name, passed in checks.items()},
            answer=candidate,
            explanation="all rules pass" if not failures else f"FAIL: {failures}",
        )

    return score


# --- LLM judge scorer --------------------------------------------------------

JUDGE_TEMPLATE = """
You are an expert reviewer of {target_language} machine translation quality
for a software user guide.

The source English document (a list of translatable segments in an XML
envelope, may contain inline HTML such as <a id=".."> <b> <i> <code>) is:

{question}

The candidate translation replies in the same XML envelope (a <document>
with <segment id="..."> children):

{answer}

The envelope itself is expected and correct — judge the translated text
inside the segments.

Requirements the translation must meet:
1. Every segment is present, in the same order, with the same id; no
   segments dropped, merged, added, or repeated.
2. Within each segment, HTML tags and their attributes match the source
   exactly — same tags, same order, no additions.
3. Text inside <b>/<i> tags is a UI label from the Wagtail admin interface.
   Where an official admin translation exists, it must be used exactly.
   Official translations for the labels in this document:
{glossary}
   Labels without an official translation are translated naturally and
   consistently.
4. Plain prose and link text are translated into fluent, formal
   {target_language}, with meaning fully preserved (no omissions, additions,
   or mistranslations). Slug-like segments (lowercase identifiers such as
   "new-in-wagtail-7-4") must be kept unchanged. Short labels may
   legitimately be identical in both languages.
5. The output contains only the translation — no commentary, reasoning, or
   code fences — and is complete (not truncated).
6. Terminology is consistent ACROSS the whole document: one term per
   concept throughout the page.

{instructions}
"""

JUDGE_INSTRUCTIONS = """
Grade the candidate:
- C: meets all requirements; accurate and fluent, with terminology consistent
  throughout the document.
- P: understandable and structurally intact, but with minor fluency,
  terminology, or accuracy issues (including minor cross-segment
  inconsistencies).
- I: violates a structural requirement (missing/duplicated segments, HTML,
  official UI label translations, extra commentary, truncation) or materially
  mistranslates.

First reason briefly about each requirement, then finish with exactly one
line: GRADE: C, GRADE: P, or GRADE: I.
"""


@task
def translation_batch_eval(
    target_language: str = "Arabic",
    lang_code: str = "ar",
    source_language: str = "English",
    judge_model: str = JUDGE_MODEL,
):
    glossary = load_glossary(lang_code)
    system_prompt = SYSTEM_PROMPT.format(
        source_language=source_language, target_language=target_language
    )
    return Task(
        dataset=load_dataset(),
        solver=[
            translator_prompt(system_prompt, glossary),
            generate(),
        ],
        scorer=[
            rule_checks(glossary),
            model_graded_qa(
                template=JUDGE_TEMPLATE.replace("{target_language}", target_language),
                instructions=JUDGE_INSTRUCTIONS,
                partial_credit=True,
                model=judge_model,
            ),
        ],
        # A 68-segment page needs a large completion budget — same as the
        # Promptfoo batch eval's max_tokens. Reasoning off: candidates would
        # otherwise burn the whole budget thinking before emitting anything
        # (observed with gemma: 16k tokens of reasoning, empty completion).
        config=GenerateConfig(temperature=0, max_tokens=16384, reasoning_effort="none"),
    )


def main():
    import argparse
    import os

    # Map the standard Scaleway env vars (e.g. from `.env`) to the ones
    # Inspect's openai-api provider reads.
    if os.environ.get("SCW_SECRET_KEY"):
        os.environ.setdefault("SCALEWAY_API_KEY", os.environ["SCW_SECRET_KEY"])
    if os.environ.get("SCW_DEFAULT_PROJECT_ID"):
        os.environ.setdefault(
            "SCALEWAY_BASE_URL",
            f"https://api.scaleway.ai/{os.environ['SCW_DEFAULT_PROJECT_ID']}/v1",
        )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        default=",".join(CANDIDATE_MODELS),
        help="comma-separated candidate models",
    )
    parser.add_argument("--judge", default=JUDGE_MODEL, help="judge model")
    parser.add_argument("--target-language", default="Arabic")
    parser.add_argument("--lang-code", default="ar", help="glossary language code")
    parser.add_argument("--limit", type=int, default=None, help="max samples")
    args = parser.parse_args()

    from inspect_ai import eval as inspect_eval

    inspect_eval(
        translation_batch_eval(
            target_language=args.target_language,
            lang_code=args.lang_code,
            judge_model=args.judge,
        ),
        model=args.models.split(","),
        limit=args.limit,
        log_dir=LOG_DIR,
    )


if __name__ == "__main__":
    main()
