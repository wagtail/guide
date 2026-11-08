# Techniques in the saved agent traces

Analyzed **6,117 benchmark attempts**: 4,356 initial runs and 1,761 failure-selected retries. **6,087 trajectories** contain 16,865 distinct recorded tool calls; 30 attempts have no saved trajectory. Missing traces are not classified as no-tool answers.

The analysis reuses the original Promptfoo URL surface classifier, but measures **requests**, not successful access. It retains failed/blocked calls and exposes missing observations. Codex script contents establish requested intent, not confirmed nested execution. The old reports’ “reached” and “grounded” counts should not be treated as equivalent to these measures.

Visible-link flags use the original normalized-page matcher: guide-version, Markdown suffix, query and fragment differences are ignored. Events distinguish exact sanitized URLs from normalized-page matches. These establish visible source candidates, not proof that the model followed a particular link.

## Native-tool techniques by model

Fractions use recorded trajectories as the denominator. Script search is included in search requests but also shown separately. “Opaque” means the wrapper prevents a direct absence claim. Positive direct counts remain lower bounds where observations are incomplete.

| Harness     | Model               | Attempts | Traces | Search requests | Script-search traces | Homepage-first | Local inspection | llms.txt requests | Sitemap requests |
| ----------- | ------------------- | -------- | ------ | --------------- | -------------------- | -------------- | ---------------- | ----------------- | ---------------- |
| claude-code | claude-fable-5-1    | 99       | 99     | 57/99           | 0                    | 4/99           | 6/99             | 0/99              | 6/99             |
| claude-code | claude-haiku-5-5    | 99       | 99     | 60/99           | 0                    | 24/99          | 17/99            | 0/99              | 0/99             |
| claude-code | claude-opus-5-5     | 99       | 99     | 43/99           | 0                    | 5/99           | 1/99             | 0/99              | 4/99             |
| claude-code | claude-sonnet-5-5   | 99       | 99     | 77/99           | 0                    | 6/99           | 0/99             | 0/99              | 0/99             |
| codex       | gpt-6-astra         | 99       | 96     | 90/96           | 90                   | Opaque         | Opaque           | Opaque            | Opaque           |
| codex       | gpt-6-luna          | 99       | 99     | 96/99           | 96                   | Opaque         | Opaque           | Opaque            | Opaque           |
| codex       | gpt-6.1-sol         | 99       | 99     | 93/99           | 93                   | Opaque         | Opaque           | Opaque            | Opaque           |
| codex       | gpt-6.1-terra       | 99       | 99     | 96/99           | 96                   | Opaque         | Opaque           | Opaque            | Opaque           |
| cursor-cli  | grok-4.7-medium     | 99       | 99     | 95/99           | 0                    | 4/99           | 30/99            | 0/99              | 1/99             |
| opencode    | deepseek-v4.1-flash | 99       | 99     | 81/99           | 0                    | 12/99          | 9/99             | 0/99              | 4/99             |
| opencode    | gemma-4-31b         | 99       | 99     | 79/99           | 0                    | 3/99           | 0/99             | 0/99              | 0/99             |
| opencode    | glm-5.3             | 99       | 99     | 78/99           | 0                    | 10/99          | 38/99            | 3/99              | 30/99            |
| opencode    | glm-5.3-flash       | 99       | 99     | 79/99           | 0                    | 10/99          | 12/99            | 2/99              | 10/99            |
| opencode    | kimi-k3             | 99       | 99     | 92/99           | 0                    | 8/99           | 13/99            | 0/99              | 6/99             |
| opencode    | mimo-v2.6-pro       | 99       | 99     | 85/99           | 0                    | 6/99           | 10/99            | 5/99              | 2/99             |
| opencode    | qwen-3.8-27b        | 99       | 99     | 84/99           | 0                    | 9/99           | 42/99            | 3/99              | 29/99            |
| vibe        | mistral-large-4     | 99       | 99     | 86/99           | 0                    | 4/99           | 1/99             | 0/99              | 1/99             |

## Question framing

These are **different questions**, not randomized paraphrases. “Site-named” has 19 questions, “site-not-named” nine, and “site-start” five. The table describes associations with wording; it does not isolate the causal effect of an instruction. Native arms only; each harness includes all its tested models.

| Harness     | Framing        | Attempts | Homepage-first | Search requests | Local inspection |
| ----------- | -------------- | -------- | -------------- | --------------- | ---------------- |
| claude-code | site-named     | 228      | 10/228         | 176/228         | 8/228            |
| claude-code | site-not-named | 108      | 0/108          | 38/108          | 16/108           |
| claude-code | site-start     | 60       | 29/60          | 23/60           | 0/60             |
| codex       | site-named     | 228      | Opaque         | 226/226         | Opaque           |
| codex       | site-not-named | 108      | Opaque         | 107/107         | Opaque           |
| codex       | site-start     | 60       | Opaque         | 42/60           | Opaque           |
| cursor-cli  | site-named     | 57       | 0/57           | 57/57           | 16/57            |
| cursor-cli  | site-not-named | 27       | 0/27           | 26/27           | 11/27            |
| cursor-cli  | site-start     | 15       | 4/15           | 12/15           | 3/15             |
| opencode    | site-named     | 399      | 3/399          | 378/399         | 59/399           |
| opencode    | site-not-named | 189      | 0/189          | 140/189         | 54/189           |
| opencode    | site-start     | 105      | 55/105         | 60/105          | 11/105           |
| vibe        | site-named     | 57       | 0/57           | 55/57           | 1/57             |
| vibe        | site-not-named | 27       | 0/27           | 19/27           | 0/27             |
| vibe        | site-start     | 15       | 4/15           | 12/15           | 0/15             |

## Recorded instructions and restrictions

Every attempt is linked to the original question, task category, arm controls and an instruction fingerprint. A fingerprint describes only recorded evidence: it does not establish equivalence between hidden harness system prompts. The full recorded system messages stay in the local instructions.jsonl; semantic review receives bounded excerpts with an explicit truncation flag.

| Harness     | Initial attempts | System text recorded | Recorded instruction profiles |
| ----------- | ---------------- | -------------------- | ----------------------------- |
| claude-code | 1188             | 0                    | 3                             |
| codex       | 792              | 785                  | 8                             |
| cursor-cli  | 99               | 0                    | 1                             |
| opencode    | 2079             | 0                    | 3                             |
| vibe        | 198              | 0                    | 2                             |

Only captured instructions and explicit arm controls can support instruction-specific explanations. Unavailable system text is not evidence that a harness had no system instructions. Tool availability, model identity and harness behavior also differ.

## Comparing techniques with outcomes

within-case-associations.csv compares feature-present and feature-absent initial attempts only where the **same model, arm and question** has both. Each eligible question contributes equally. These remain observational associations: a model may change approach because a question is difficult. For this table, missing trajectories, opaque wrappers, unresolved shell targets and missing observations are excluded; their full counts remain in the inventory and other tables.

There are 88 model/arm/technique comparisons with at least one matched question. Small cells are for inspection, not significance claims.

## Initial versus retry paths

retry-pairs.jsonl links every retry to its original failure and lists added/removed recorded features. Retries are analyzed separately throughout because they are selected failures. A changed feature is not proof that a changed strategy caused recovery.

| Retry pairs | Both trajectories present | Recovered failures |
| ----------- | ------------------------- | ------------------ |
| 1761        | 1731                      | 162                |

## Files and evidence review

- trials.jsonl: one record per attempt, question, instructions, grade, timing and technique flags.
- events.jsonl: event IDs, grouped step order, tool names, direct versus script requests, statuses, sanitized URL targets and link provenance. Raw response bodies are omitted.
- by-arm.csv, by-framing.csv and by-case.csv: separate initial/retry counts, trace coverage and techniques.
- instructions.jsonl: local recorded system text and arm controls, indexed by fingerprint.
- retry-pairs.jsonl: exact initial/retry pairing with observed feature changes.
- semantic-inputs/ and analysis-jobs/: whitelisted inputs and Harbor-native rubric review; keep model assessments separate from deterministic observations.

No new candidate executions or grading changes are made by this pipeline. No proxy headers were captured in these runs, so HTTP Accept negotiation, redirect success and browser-only capabilities cannot be inferred from requests. Explicit Markdown formats are requests, not proof of served content. A URL with no visible earlier source is not automatically a guess. Shell analysis recognizes a conservative subset of literal curl and local commands; unrecognized shell constructs are not interpreted or executed.
