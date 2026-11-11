# Trying published prompt-improvement prompts

Two published prompts were run against 16 existing sanitized traces on 11 November 2026. They produced useful hypotheses, but also demonstrated why their suggestions need review: GEPA copied task answers into its proposed instructions, while TextGrad made several errors about the evidence. **Neither proposal was applied, and no improvement in benchmark performance has been measured.**

## Published prompts used

- [GEPA's instruction-proposal template](https://github.com/gepa-ai/gepa/blob/ce5b0d6e3d6af6c6dbec6de2c54536bbb961d309/src/gepa/strategies/instruction_proposal.py) asks a model to revise instructions from examples, responses and feedback. Its default explicitly encourages including domain facts from examples. We ran that template, filling its two slots ourselves. This was one proposal call, not GEPA's candidate evaluation or selection algorithm.
- [TextGrad's backward prompts](https://github.com/zou-group/textgrad/blob/75e912e210864b61999781778cdf756d4468120f/textgrad/autograd/llm_backward_prompts.py) ask for criticism of a text variable in light of downstream feedback. We used its original system, conversation, chain-feedback and variable-review templates. The objective and historical examples were project-specific slot values. This was one feedback call, not TextGrad's optimization loop.

The verbatim template strings, pinned source revisions and MIT license notices are in [prompt-improvement](prompt-improvement/manifest.json). GEPA examples were inserted as JSON instead of its library's Markdown renderer. TextGrad templates were assembled without installing the optimization package. This reused native Claude Code; no agent adapter was added.

[OpenAI's prompt optimizer documentation](https://developers.openai.com/api/docs/guides/prompt-optimizer) also describes using annotations, critiques and grader results, but it is a hosted workflow rather than the reusable source prompt tested here. Its current documentation announces retirement of the dataset-backed Evals platform. It was researched, not run. Its advice to evaluate and manually review resulting prompts remains applicable.

## What was run

Both calls used `claude-haiku-5-5` through Claude Code, with `--bare`, an isolated configuration directory, all tools disabled, no MCP connections, no session persistence and a $0.60 budget cap per call. Only the selected provider credential was loaded into the process environment. The credential was not part of either prompt or artifact.

The existing citation-review sample contains 16 diagnostic records: Claude Code 4, Codex 3, Cursor 2, OpenCode 5, Vibe 2; baseline 4, native 6, native+MCP 4, web 2. Nine have an original passing aggregate grade and seven do not. This is a deliberately selected diagnostic sample, **not representative prevalence**. Four records omit middle calls; 12 contain truncated observation excerpts. No final answer was truncated. Missing evidence stays explicitly marked.

Each review received the original question, answer, controls, framing, case, model/harness, bounded observations, evidence IDs, missingness flags and aggregate grade/error flags. No per-assertion grader explanations or complete harness system prompts were supplied. A failed aggregate grade therefore does not establish a cause. No fresh website content was substituted for historical observations.

The original task instruction is just `{{prompt}}`, with each question passed through unchanged. The review target was a possible **additional prefix in a separate future arm**, not a change to the original questions or existing comparisons.

| Review             | Input tokens including cache creation | Output tokens |              Wall time | CLI-reported estimated cost |
| ------------------ | ------------------------------------: | ------------: | ---------------------: | --------------------------: |
| GEPA template      |                               106,418 |         3,065 |               16.356 s |                 $0.07417325 |
| TextGrad templates |                               107,282 |         1,922 |               14.773 s |                 $0.07185575 |
| Total              |                               213,700 |         4,987 | Calls ran concurrently |                 $0.14602900 |

Each completed in one turn, with zero search/fetch requests. Costs are the CLI's list-price estimates, not billing reconciliation. Input totals include 213,692 cache-creation tokens across the calls; reading the uncached `input_tokens` field alone would incorrectly suggest just eight input tokens. Raw usage is retained in the two `*-usage.json` files. Timing compares these two review calls only.

## Suggestions worth testing

**Make source attribution match the evidence available.** Both reviews favor distinguishing retrieved evidence from memory and unverified links. The original no-tools answer `6965a0c277b10802` already disclosed that it could not browse, so the proposed instruction does not introduce that behavior from scratch. Its uncertain links still illustrate the usefulness of separately grading honesty, citation validity and answer correctness. Search snippets can support limited claims; they should not automatically count as full-page reads.

**Stop repeating unavailable actions and return a bounded answer.** TextGrad highlights repeated approval denials in `30079b324c58f114` and the usage-limit response followed by extensive exploration in `0491ca55c0f95e16`. These support trying explicit fallback behavior. A prompt cannot remove a provider quota, enable a denied tool or guarantee a final answer before termination. The latter trace omits 22 middle calls, so the displayed history is incomplete.

**Keep editor advice within the requested scope.** Several traces add source-code or developer information to editor questions. A concise editor-first answer is a reasonable candidate. A blanket ban on developer sources would be too strong: troubleshooting can require them, and the original question may merely request official documentation.

**Report temporal limits for release questions.** The failed aggregate grade for `27145ad5cea5f3e8` does not prove its retrieved release information was wrong. That answer already states the page date and limitations of the release index. Inspect the specific grader checks and their expected date/version before changing the model's instructions.

## Suggestions and claims rejected during review

The complete generated outputs are preserved as [GEPA output](prompt-improvement/gepa-output.txt) and [TextGrad output](prompt-improvement/textgrad-output.txt). They are untrusted proposals, not authoritative Wagtail guidance. The [review CSV](PROMPT_IMPROVEMENT_REVIEW.csv) records evidence and dispositions for selected claims; it is not an exhaustive error-rate estimate.

- GEPA produced a long domain-facts section containing answers to roles, scheduling, reports, shortcuts, content checks and release questions. Injecting that into reruns would teach the test answers and compromise the benchmark. It also names `guide.wagtail.org` for every question, removing the original distinction between site-named and site-not-named discovery.
- GEPA recommends deriving alternate `/en/` and `/en-latest/` paths after failures, while also warning against inventing URLs. Prefer observed links, redirects or index results; do not globally rewrite URL shapes from this sample.
- TextGrad calls `42383817403a7fe0` a passing run. The supplied `original_grader_passed` is **false**.
- TextGrad says `3e49675d44f7f2b0` used one search and one fetch. Its complete supplied evidence contains **two searches and one fetch**.
- TextGrad describes `01ee2acc8198192f` as presenting a sourced final answer. Its actual answer field is empty. Answer-like text occurs inside a malformed tool-name field. That is a tool serialization/recovery issue; it is not evidence of a final delivered citation.
- TextGrad describes `0a64774c4d8dea93` as reporting that no dedicated page was documented. Its final answer actually states that the official guide explicitly says deleted documents cannot be recovered, and the final fetch contains that warning. The recommendation's example is misleading.

These are concrete reasons to check optimizer statements against structured fields and event IDs. Plausible prose is not sufficient validation.

## Next experiment, if pursued

Create a new, clearly labeled instruction arm with a short domain-independent prefix: obey available tool restrictions, separate observed evidence from memory, avoid inventing sources, and stop after repeated identical access failures. Keep the 33 existing questions, framing and original arms unchanged. Exclude all example answers, exact guide URLs and release facts from the prefix.

Use development cases for proposing changes and untouched case families for evaluation; holding out only repeats of the same question is insufficient. Compare paired success, unsupported attribution, final-answer availability, tool calls, cost and time. Review per-check failures before optimizing a potentially stale grader. No such candidate evaluation was performed in this pilot.

## Reuse and audit artifacts

- [Manifest](prompt-improvement/manifest.json): source revisions, sample IDs, hashes, configuration and scope.
- [GEPA template](prompt-improvement/gepa-template.txt): substitute `<curr_param>` and `<side_info>`.
- [TextGrad system template](prompt-improvement/textgrad-system.txt), [conversation template](prompt-improvement/textgrad-conversation-template.txt) and [user template](prompt-improvement/textgrad-user-template.txt): fill the named slots with the current instruction, examples and explicit feedback.
- [Run configuration](prompt-improvement/run-config.json): exact CLI options, system/context strings and TextGrad slot definitions used here.
- Rendered prompts, the whitelisted sample and raw CLI results remain in `~/.cache/guide-agent-eval/harbor/trace-analysis-followups-2026-11-11/prompt-improvement/`. Their hashes are in the manifest. Raw session directories and credentials were not published.

The two prompts have different instructions and output formats, and each ran once. This trial establishes that the templates can generate reviewable proposals from these traces. It does not rank the optimizers or demonstrate a success-rate gain.
