# Paid integration pilots — November 2026

One case (`info-schedule-page`), one repeat per reported arm, one model per harness. At the time of this pilot, the other ten requested model/harness pairs were configured, with credential availability checked, but had not had paid inference tests. The active matrix now excludes Cursor Gemini and Muse, as requested; Cursor runs use Grok 4.7 only. These results validate the integration; they are not estimates of full-suite success rates or a model ranking.

| Model / arm                 | Result | Agent seconds | Candidate USD | Judge USD |
| --------------------------- | ------ | ------------: | ------------: | --------: |
| opencode-deepseek--native   | Pass   |         13.64 |      0.001648 |  0.003701 |
| opencode-deepseek--baseline | Fail   |          5.30 |      0.000187 |  0.003575 |
| opencode-deepseek--web      | Pass   |          9.84 |      0.000903 |  0.003929 |
| claude-haiku--native        | Pass   |         17.91 |      0.014424 |  0.004516 |
| claude-haiku--baseline      | Fail   |          6.73 |      0.000904 |  0.005048 |
| codex-luna--native          | Pass   |         17.49 |      0.003429 |  0.003436 |
| codex-luna--baseline        | Fail   |         11.92 |      0.001618 |  0.003461 |
| cursor-grok--native         | Pass   |         42.81 |       unknown |  0.004099 |
| vibe-large--native          | Pass   |         13.65 |      0.014149 |  0.003694 |
| vibe-large--baseline        | Fail   |         13.89 |      0.015090 |  0.004564 |
| claude-haiku--web           | Pass   |         15.76 |      0.014190 |  0.004568 |

Costs above cover the selected trials and their latest grading pass only. Debugging runs and earlier grading passes also incurred charges. Candidate costs are reported token-price estimates; Cursor cost coverage is missing. See the [cost qualifications](README.md#reading-the-results).

Using Harbor’s own cost estimator with the saved Grok usage and [published Cursor list prices](https://cursor.com/docs/models-and-pricing) gives **$0.119052** for its native run. This is a retrospective token-price estimate, not a measured charge; the original artifacts retain their unknown cost. The active matrix supplies Grok’s rates via Harbor’s native pricing option.

## Controls and compatibility

- Claude, Codex and OpenCode baselines recorded zero tool calls. The corrected Vibe baseline recorded three discovery operations, each returning zero tools and zero connector notices, and no usable tool calls.
- Cursor baseline experiments still executed web search/fetch despite deny-all hooks installed in both user and project configuration. They are invalid controls and are excluded above. The runner now reports Cursor baselines as unavailable.
- Earlier Codex and Vibe controls also failed the tool audit. Their outputs are preserved as execution errors, not scored as ordinary wrong answers.
- Vibe 3 changed its log format. The shim maps exported messages, reasoning and effects to the format Harbor already converts, preserving tool observations and usage. The native Vibe trajectory above was regenerated from its saved export after fixing that mapping; the candidate was not rerun.
- Both web-only pilots (Claude and OpenCode) passed. Claude recorded only WebSearch/WebFetch calls.
- Earlier runs used Harbor 0.23.0; corrected Codex/Vibe controls and the final exporter use 0.25.0. Installed CLI versions were Claude 2.1.318, Codex 0.166.0, Cursor 2026.10.22-27dcf5f, OpenCode 1.19.5 and Vibe 3.1.0. Run a fresh matched experiment for comparisons.

## Local artifacts

Trajectories, raw logs, grades and per-experiment CSVs remain outside the repository under `~/.cache/guide-agent-eval/harbor/`:

- `pilot-2026-11-05b/`.
- `claude-pilot-2026-11-05/`.
- `claude-web-pilot/`.
- `codex-pilot-2026-11-05/` — use `codex-luna--native` only.
- `codex-baseline-fixed/`.
- `cursor-pilot-fixed-2026-11-05/` — use `cursor-grok--native` only.
- `vibe-final-pilot/` — use `vibe-large--native` only.
- `vibe-no-connectors/`.

`comparison-2026-11-05/` contains the original prepared matrix: 34 supported jobs × 33 cases × 3 repeats. It has **not** been launched. Cursor baseline and unsupported web-only combinations are listed in its manifest. This export predates the Grok-only Cursor restriction and must not be launched unchanged. Prepare a fresh matrix from the current configuration.

## Additional model smoke tests

A second batch tested the five remaining model pairs on the same scheduling question, with one repeat per supported arm. Harbor 0.25.0 used Codex 0.166.0 and OpenCode 1.19.5, at concurrency one. All 12 candidates completed; seven passed, four failed answer assertions, and one was excluded by the no-tools audit. There were no judge errors. These single-question results establish integration behavior, not comparative quality.

| Model / arm | Result | Agent seconds | Candidate USD | Judge USD |
| --- | --- | ---: | ---: | ---: | ---: |
| codex-sol--native | Pass | 22.73 | 0.066956 | 0.003725 |
| codex-sol--baseline | Fail | 14.72 | 0.028304 | 0.004327 |
| codex-terra--native | Pass | 8.11 | 0.023007 | 0.003359 |
| codex-terra--baseline | Fail | 8.50 | 0.014097 | 0.006518 |
| codex-astra--native | Pass | 10.60 | 0.311204 | 0.003815 |
| codex-astra--baseline | Fail | 14.83 | 0.139068 | 0.004910 |
| opencode-glm--native | Pass | 17.41 | 0.002302 | 0.003788 |
| opencode-glm--baseline | Invalid control | 12.52 | 0.001055 | not called |
| opencode-glm--web | Pass | 7.72 | 0.001254 | 0.003888 |
| opencode-mimo--native | Pass | 8.92 | 0.005765 | 0.003764 |
| opencode-mimo--baseline | Fail | 4.64 | 0.000890 | 0.002864 |
| opencode-mimo--web | Pass | 7.87 | 0.003333 | 0.003836 |

Total reported usage: $0.5972 candidate cost and $0.0448 judging ($0.6420 combined).

GLM's no-tools trial emitted a malformed `WebFetch萃*` call. OpenCode rejected it with `Model tried to call unavailable tool 'invalid'. Available tools: .`; no tool executed. The strict replay audit rejects attempted tool calls as well as successful ones, so this trial remains an execution/control error instead of a scored answer. No control or grader was relaxed to make the pilot pass. The other four baselines recorded zero tool calls.

Artifacts: `~/.cache/guide-agent-eval/harbor/remaining-smoke-2026-11-05/`. The separate `remaining-comparison-2026-11-05/` batch contains the current 20 non-Claude jobs × 33 cases × 3 repeats (1,980 runs). It was launched on 5 November 2026 at concurrency three, with grading after each completed arm. It includes only Grok 4.7 for Cursor. Its `run.log`, `grading-monitor.log` and per-job results track progress; `comparison.csv` updates after each graded arm.

## Neuralwatt expansion — 6 November 2026

Four more standard models completed the same scheduling smoke question with native tools through OpenCode 1.19.5. All four passed without execution, grading or tool-audit errors. The requested unlisted `kimi-k3.1-pro` preview also passed a separate native-tool trial. These checks validate integration, not general reliability.

| Model         | Result | Agent seconds | Candidate USD | Judge USD |
| ------------- | ------ | ------------: | ------------: | --------: |
| glm-5.3       | Pass   |         19.29 |      0.023604 |  0.003629 |
| qwen-3.8-27b  | Pass   |         30.95 |      0.027386 |  0.003794 |
| gemma-4-31b   | Pass   |         22.69 |      0.004589 |  0.003567 |
| kimi-k3       | Pass   |         19.78 |      0.078817 |  0.004412 |
| kimi-k3.1-pro | Pass   |         14.66 |       unknown |  0.003808 |

The four standard-model smoke tests initially inherited a general Neuralwatt environment key. Credential checks then found that the matching GLM and Qwen file keys accepted inference requests, while the Gemma and Kimi file keys returned HTTP 401. The GLM key was verified as an authorized fallback for Gemma, Kimi K3 and Kimi K3.1 Pro. The full expansion service explicitly removes the inherited `NEURALWATT_API_KEY`: GLM and Qwen use their matching file keys, while Gemma and Kimi use the GLM file key. The preview row above is the repeat with that explicit fallback. Its first inherited-key trial also passed in 19.40 seconds and is preserved separately.

The preview has no price in the public catalog, and Harbor recorded its candidate cost as unknown. It is excluded from the full matrix. The direct credential probes and initial preview trial are additional calls, excluded from the table above.

The four standard models add **12 jobs × 33 questions × 3 repeats = 1,188 runs**, bringing the main matrix to **17 model/harness pairs and 4,356 runs**. The expansion is queued behind the original remaining batch so full-suite concurrency stays at three; its grading runs after each completed arm. The existing cases, tool arms, grading and source hash are unchanged.

Artifacts under `~/.cache/guide-agent-eval/harbor/`:

- `neuralwatt-expansion-smoke-2026-11-06/`: four native smoke tests and their grades.
- `neuralwatt-expansion-comparison-2026-11-06/`: queued full expansion; current services and logs are recorded in `launch-matched-keys.json`.
- `kimi-preview-smoke-2026-11-06/`: initial inherited-key preview trial.
- `kimi-preview-matched-key-2026-11-06/`: stopped attempt after the matching file key failed the direct authentication check.
- `kimi-preview-fallback-key-2026-11-06/`: passing preview trial with the explicit GLM fallback key.
- `neuralwatt-expansion-key-checks-2026-11-06.json` and `neuralwatt-expansion-fallback-checks-2026-11-06.json`: credential labels and HTTP status only; no key values.
- `neuralwatt-catalog-2026-11-06.json`: public catalog snapshot, including prices and reasoning defaults.
