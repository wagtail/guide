# Translation eval with Inspect AI

Prototype replacement for the custom eval suite in `scripts/eval/`, built on
[Inspect AI](https://inspect.aisi.org.uk/). Inspect provides the runner
(parallelism, retries, rate limiting), multi-model comparison, structured eval
logs, and a results UI — the only project code is `translation_task.py`:
the task definition, a stdlib-only rule scorer, and an LLM-judge scorer.

It evaluates the translator behaviour defined in `apps/core/translator.py`
(same system prompt, glossary injection, temperature 0) without needing Django
or the database.

## Whole-page eval (`translation_batch_task.py`)

`translation_batch_task.py` is the document-level variant: each sample is an
ENTIRE page — all segments translated in ONE LLM request, wrapped in an XML
envelope (`<document>` with `<segment id="...">` children). Both the source
and the candidate's reply are whole documents, which is what makes
page-wide terminology consistency gradeable: the judge checks that one term
per concept holds ACROSS segments, not just within each paragraph.

-   Dataset: `prompts/evals/translations-batch/documents.json` (generated
    from real guide content by `build_documents.py` in the same directory).
-   Prompt: the production system prompt + whole-document glossary + XML
    format instructions + a worked few-shot example, mirroring the Promptfoo
    batch eval (`prompts/evals/translations-batch/translation_prompt.py`).
-   `rule_checks` decodes the envelope and verifies, per segment: ids in
    order and complete (`envelope`), inline tag/attribute structure (`tags`),
    official `<b>`/`<i>` label translations (`glossary`), no truncation
    (`no_trunc`), plus no commentary/bleed around the envelope (`no_bleed`).
-   The LLM judge grades the whole document with a cross-segment
    terminology-consistency requirement (requirement 6 in its rubric).

Run it with:

```sh
just eval-translations-batch                    # all candidates, Arabic
just eval-translations-batch --limit 1          # one page, quick smoke run
```

Per-segment results for the same pages come from the Promptfoo baseline
(`just eval-batch-baseline`), so document-level vs per-segment quality is
directly comparable.

## Per-segment eval (`translation_task.py`)

`translation_task.py` below is the original per-segment eval: each sample is
a single wagtail-localize segment, translated in isolation — the same request
shape production currently uses.

## Setup

The script is self-contained: a [PEP 723](https://peps.python.org/pep-0723/)
inline-metadata script with a `uv run` shebang, so `uv` resolves `inspect-ai`
and `openai` on first run — nothing to install beyond `uv`.

Candidate models and the judge are declared at the top of
`translation_task.py` (`CANDIDATE_MODELS`, `JUDGE_MODEL`). Scaleway's
Generative APIs are OpenAI Chat Completions compatible and addressed via
Inspect's `openai-api/scaleway/<model>` naming; credentials are picked up from
the standard `SCW_SECRET_KEY` and `SCW_DEFAULT_PROJECT_ID` environment
variables (e.g. from `.env`, which `just` loads automatically).

## UI label glossary

UI labels in `<b>`/`<i>` tags must reuse the official Wagtail admin interface
translations — e.g. Icelandic `Collection` = `Safn` — so guide content and the
interface always use the same terms. `apps/core/translator.py` reads these
live from Django's merged translation catalog (which includes Wagtail's own
`.po` files) and injects a per-batch glossary into the system prompt. The eval
mirrors this exactly, from a JSON export of the same catalog:

```sh
just eval-glossary ar        # writes prompts/evals/translations-inspect_ai/glossary/ar.json
just eval-glossary ar is fr  # one file per language code
```

Labels without an official translation are translated freely.

## Run

```sh
just eval-translations                          # all candidates, Arabic
just eval-translations --limit 2                # quick smoke run
just eval-translations --target-language Icelandic --lang-code is
just eval-translations --models openai-api/scaleway/qwen3.6-35b-a3b
just eval-translations --judge openai-api/scaleway/mistral-medium-3.5-128b
```

Then browse per-sample transcripts, scores, and token usage:

```sh
just eval-view
```

Logs land in `prompts/evals/translations-inspect_ai/logs/` (gitignored; `.eval` files are also
readable programmatically with `inspect_ai.log.read_eval_log`).

## What's scored

In both evals:

-   `rule_checks` — deterministic, stdlib `html.parser` only. Per-segment eval:
    HTML tag/attribute structure, glossary compliance for `<b>`/`<i>` labels
    (position-wise, exact official translation), no truncation, no reasoning
    bleed. Whole-page eval: the same checks, run on each segment of the
    decoded envelope, plus envelope completeness/order (`envelope`). Reported
    per rule (accuracy ± stderr).
-   `model_graded_qa` — LLM judge (`glm-5.2` by default) grading
    accuracy/fluency/rule compliance as C/P/I with partial credit. The judge
    prompt includes the glossary for the sample (via sample metadata). The
    judge is deliberately not one of the candidates, to avoid self-preference.
    The whole-page judge additionally requires terminology to be consistent
    ACROSS the document — one term per concept page-wide.

## Notes / differences from the custom suite

-   The old "keep `<b>`/`<i>` text in English" rule is replaced by glossary
    compliance, matching the translator's actual behaviour.
-   Grading is per-candidate (C/P/I) rather than pairwise A/B/C ranking. Inspect
    shuffles nothing because there is no position to bias; comparison happens
    across eval runs in the viewer. Pairwise ranking is possible but needs a
    custom scorer again — start without it.
-   Rules that don't apply to a sample (e.g. no glossary term in the source)
    count as a pass rather than being excluded from the denominator.
-   The per-segment dataset is `prompts/evals/translations/segments.yaml`,
    shared with the Promptfoo eval: segments extracted verbatim from real
    guide content (`prompts/content/en/how-to-guides/manage-documents.md` and
    `prompts/content/en/releases/new-in-wagtail-7-4.md`), in the HTML form the
    translator receives from wagtail-localize. Each entry is a Promptfoo test
    case (`description`, `vars.text`, `metadata.id`/`metadata.source`);
    `translation_task.py` maps them to Inspect Samples. Regenerate from live
    page content with `export_segments.py` (see its docstring), or grow the
    file as regressions are found.
-   The whole-page dataset is
    `prompts/evals/translations-batch/documents.json` — the same guide pages
    as the Promptfoo batch eval, so batch results are comparable across both
    harnesses. Rebuild with
    `uv run python prompts/evals/translations-batch/build_documents.py`.

