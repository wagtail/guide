#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["inspect-ai", "openai", "pyyaml"]
# ///
"""
Inspect AI eval for the LLM translator in apps/core/translator.py.

Replaces the hand-rolled collect/check/judge/summarize pipeline: Inspect
provides the runner, parallelism, retries, per-model comparison, log storage,
and a results viewer (`inspect view`). This file only defines the task, a
deterministic rule scorer, and an LLM-judge scorer.

Candidate and judge models are declared in CANDIDATE_MODELS / JUDGE_MODEL
below. Credentials come from the standard Scaleway environment variables
(SCW_SECRET_KEY, SCW_DEFAULT_PROJECT_ID), e.g. via the project `.env`.

UI labels in <b>/<i> tags are held to the official Wagtail admin translations
(e.g. Icelandic "Collection" = "Safn"), mirroring the glossary injection in
apps/core/translator.py. Export the glossary for a language first:

    just eval-glossary ar

Run it directly (uv resolves the inline dependencies):

    ./prompts/evals/translations-inspect_ai/translation_task.py
    ./prompts/evals/translations-inspect_ai/translation_task.py --limit 2 --target-language Icelandic --lang-code is

or via just:

    just eval-translations
    just eval-view
"""

import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageSystem, GenerateConfig
from inspect_ai.scorer import (
    Score,
    Target,
    accuracy,
    model_graded_qa,
    scorer,
    stderr,
)
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
# Segment dataset shared with the Promptfoo eval (Promptfoo test-case shape).
SEGMENTS_PATH = Path(__file__).parents[1] / "translations" / "segments.yaml"


def load_dataset():
    cases = yaml.safe_load(SEGMENTS_PATH.read_text(encoding="utf-8"))
    return MemoryDataset(
        [
            Sample(
                id=case["metadata"]["id"],
                input=case["vars"]["text"],
                metadata={"description": case["description"], **case["metadata"]},
            )
            for case in cases
        ]
    )


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

UI_LABEL_RE = re.compile(r"<(b|i)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)


def ui_terms(html: str) -> list[str]:
    """Unique <b>/<i> label texts, in order — as in LLMTranslator."""
    terms = []
    for _tag, text in UI_LABEL_RE.findall(html or ""):
        term = unescape(re.sub(r"<[^>]+>", "", text)).strip()
        if term and term not in terms:
            terms.append(term)
    return terms


def load_glossary(lang_code: str) -> dict[str, str]:
    path = GLOSSARY_DIR / f"{lang_code}.json"
    if not path.exists():
        print(
            f"WARNING: no glossary at {path} — UI label consistency will not "
            f"be prompted or scored. Generate it with: just eval-glossary {lang_code}"
        )
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


# --- Solver: per-sample system prompt with glossary, as in production --------


@solver
def translator_prompt(system_prompt: str, glossary: dict[str, str]):
    """Prepend the translator system prompt, plus the glossary entries for the
    UI labels present in this sample (mirrors LLMTranslator.get_messages)."""

    async def solve(state: TaskState, generate):
        matched = {
            term: glossary[term]
            for term in ui_terms(state.input_text)
            if term in glossary
        }
        lines = "\n".join(f"- {src} = {dst}" for src, dst in matched.items())
        # Stash for the judge template ({glossary} via sample metadata).
        state.metadata["glossary"] = lines or "(none for this segment)"
        prompt = system_prompt
        if matched:
            prompt += GLOSSARY_PROMPT.format(glossary=lines)
        state.messages.insert(0, ChatMessageSystem(content=prompt))
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
    """Format rules from the translator system prompt, checked mechanically.

    html_tags  same tag sequence + attributes as the source
    glossary   <b>/<i> labels use the official Wagtail admin translation
    no_trunc   output not suspiciously short vs source
    no_bleed   no code fences or commentary preamble

    Checks that don't apply to a sample (e.g. no glossary term in the source)
    score 1.
    """

    async def score(state: TaskState, target: Target) -> Score:
        source = state.input_text
        candidate = (state.output.completion or "").strip()
        src = _parse(source)
        cand = _parse(candidate)

        # Position-wise comparison of <b>/<i> labels against the glossary.
        expected = [
            (i, text, glossary[text])
            for i, text in enumerate(src.bold_texts)
            if text in glossary
        ]
        if not expected:
            glossary_ok = True
        elif len(cand.bold_texts) != len(src.bold_texts):
            glossary_ok = False
        else:
            glossary_ok = all(
                cand.bold_texts[i] == official for i, _text, official in expected
            )

        checks = {
            # Strict equality both ways: also fails when the model invents
            # tags in a plain-prose source (a known failure mode).
            "html_tags": src.tags == cand.tags,
            "glossary": glossary_ok,
            "no_trunc": len(candidate) >= TRUNC_MIN_RATIO * len(source),
            "no_bleed": bool(candidate) and not BLEED_RE.search(candidate[:200]),
        }
        failures = [name for name, passed in checks.items() if not passed]
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

SOURCE (English, may contain inline HTML such as <a id=".."> <b> <i> <code>):
{question}

CANDIDATE {target_language} TRANSLATION:
{answer}

Requirements the translation must meet:
1. HTML tags and their attributes match the source exactly — same tags, same
   order, no additions.
2. Text inside <b>/<i> tags is a UI label from the Wagtail admin interface.
   Where an official admin translation exists, it must be used exactly.
   Official translations for the labels in this segment:
{glossary}
   Labels without an official translation are translated naturally and
   consistently.
3. Plain prose and link text are translated into fluent, formal
   {target_language}, with meaning fully preserved (no omissions, additions,
   or mistranslations).
4. The output contains only the translation — no commentary, reasoning, or
   code fences — and is complete (not truncated).
5. Terminology is consistent: one term per concept.

{instructions}
"""

JUDGE_INSTRUCTIONS = """
Grade the candidate:
- C: meets all requirements; accurate and fluent.
- P: understandable and structurally intact, but with minor fluency,
  terminology, or accuracy issues.
- I: violates a structural requirement (HTML, official UI label translations,
  extra commentary, truncation) or materially mistranslates.

First reason briefly about each requirement, then finish with exactly one
line: GRADE: C, GRADE: P, or GRADE: I.
"""


@task
def translation_eval(
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
        config=GenerateConfig(temperature=0),
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
        translation_eval(
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
