## Results per arm, 5 repeat(s) (mean ± SD across repeats)

| Arm                          | Runs | Pass    | Facts | Citation | Judge | Cost/answer | Duration | Tool calls |
| ---------------------------- | ---- | ------- | ----- | -------- | ----- | ----------- | -------- | ---------- |
| claude-code/fable-5.2        | 165  | 96% ± 3 | 99%   | 97%      | 99%   | 20.9¢       | 24s      | 4.3        |
| claude-code/haiku-5.5        | 165  | 84% ± 5 | 98%   | 92%      | 93%   | 1.6¢        | 22s      | 3.4        |
| claude-code/opus-5.5         | 165  | 98% ± 1 | 99%   | 99%      | 100%  | 9.9¢        | 24s      | 4.0        |
| claude-code/sonnet-5.5       | 165  | 93% ± 1 | 99%   | 96%      | 98%   | 4.9¢        | 20s      | 4.3        |
| codex/luna-6                 | 165  | 92% ± 5 | 98%   | 92%      | 98%   | 0.4¢        | 12s      | 2.1        |
| codex/sol-6.1                | 165  | 99% ± 1 | 100%  | 99%      | 100%  | 5.2¢        | 9s       | 1.3        |
| opencode/deepseek-v4.1-flash | 165  | 89% ± 3 | 96%   | 92%      | 93%   | 0.0¢        | 15s      | 2.4        |
| opencode/qwen-3.8-27b        | 165  | 96% ± 3 | 100%  | 98%      | 99%   | 1.2¢        | 49s      | 3.7        |

## Median of 5 runs per case

| Arm                          | Cases passed | Median duration | Suite duration | Median cost | Suite cost |
| ---------------------------- | ------------ | --------------- | -------------- | ----------- | ---------- |
| claude-code/fable-5.2        | 32/33        | 23s             | 12.8 min       | 20.40¢      | $6.88      |
| claude-code/haiku-5.5        | 30/33        | 22s             | 12.2 min       | 1.62¢       | $0.53      |
| claude-code/opus-5.5         | 32/33        | 23s             | 13.0 min       | 9.68¢       | $3.23      |
| claude-code/sonnet-5.5       | 32/33        | 20s             | 10.5 min       | 4.71¢       | $1.62      |
| codex/luna-6                 | 31/33        | 10s             | 6.6 min        | 0.29¢       | $0.11      |
| codex/sol-6.1                | 33/33        | 8s              | 5.0 min        | 4.75¢       | $1.72      |
| opencode/deepseek-v4.1-flash | 30/33        | 10s             | 6.7 min        | -           | -          |
| opencode/qwen-3.8-27b        | 32/33        | 39s             | 25.9 min       | 0.92¢       | $0.36      |

## Pass rate by task

| Task            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge          | 100%                  | 80%                   | 100%                 | 80%                    | 100%         | 100%          | 80%                          | 100%                  |
| information     | 96%                   | 91%                   | 99%                  | 95%                    | 93%          | 100%          | 88%                          | 99%                   |
| negative        | 100%                  | 100%                  | 100%                 | 100%                   | 100%         | 100%          | 100%                         | 100%                  |
| releases        | 93%                   | 67%                   | 100%                 | 93%                    | 100%         | 100%          | 87%                          | 100%                  |
| troubleshooting | 98%                   | 78%                   | 92%                  | 90%                    | 80%          | 98%           | 90%                          | 88%                   |

## Pass rate by framing

| Framing        | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| -------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| site-named     | 98%                   | 81%                   | 100%                 | 98%                    | 100%         | 99%           | 95%                          | 99%                   |
| site-not-named | 91%                   | 82%                   | 91%                  | 84%                    | 73%          | 100%          | 73%                          | 89%                   |
| site-start     | 100%                  | 96%                   | 100%                 | 92%                    | 96%          | 100%          | 96%                          | 100%                  |

## Surfaces reached (share of runs; counts are per run)

| Column                            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| web_search_used                   | 0%                    | 77%                   | 4%                   | 10%                    | 97%          | 97%           | 40%                          | 79%                   |
| homepage_reached                  | 10%                   | 22%                   | 10%                  | 43%                    | 3%           | 4%            | 24%                          | 22%                   |
| docs_reached                      | 85%                   | 62%                   | 82%                  | 77%                    | 10%          | 27%           | 55%                          | 63%                   |
| markdown_page_reached             | 0%                    | 2%                    | 0%                   | 0%                     | 0%           | 0%            | 1%                           | 0%                    |
| llms_txt_reached                  | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 2%                           | 1%                    |
| llms_full_reached                 | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 1%                           | 0%                    |
| skill_reached                     | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| mcp_used                          | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| sitemap_reached                   | 4%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 1%                           | 0%                    |
| robots_txt_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| well_known_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| openapi_reached                   | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| dev_docs_reached                  | 14%                   | 15%                   | 13%                  | 11%                    | 3%           | 2%            | 9%                           | 21%                   |
| github_copy_reached               | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| external_reached                  | 1%                    | 1%                    | 0%                   | 0%                     | 1%           | 0%            | 1%                           | 4%                    |
| answer_cites_guide                | 87%                   | 84%                   | 90%                  | 87%                    | 81%          | 88%           | 82%                          | 87%                   |
| answer_grounded                   | 86%                   | 62%                   | 83%                  | 78%                    | 5%           | 23%           | 44%                          | 53%                   |
| citations_not_fetched             | 0.0                   | 0.4                   | 0.2                  | 0.4                    | 1.3          | 1.2           | 0.6                          | 0.5                   |
| versioned_url_reached             | 84%                   | 12%                   | 78%                  | 38%                    | 0%           | 0%            | 32%                          | 0%                    |
| answer_cites_versioned_url        | 54%                   | 23%                   | 59%                  | 23%                    | 0%           | 0%            | 5%                           | 0%                    |
| legacy_editor_manual_reached      | 1%                    | 1%                    | 4%                   | 7%                     | 2%           | 0%            | 1%                           | 2%                    |
| answer_cites_legacy_editor_manual | 0%                    | 5%                    | 1%                   | 3%                     | 5%           | 0%            | 1%                           | 1%                    |
| fetch_errors                      | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.3                          | 0.9                   |
| curl_calls                        | 0.0                   | 0.0                   | 0.0                  | 0.1                    | 0.0          | 0.0           | 0.1                          | 0.0                   |
| permission_denials                | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.0                          | 0.0                   |

## Judge couldn't tell (passed as UNKNOWN, review by hand)

| Arm                          | Case               |
| ---------------------------- | ------------------ |
| claude-code/fable-5.2        | releases-8-0-api   |
| opencode/deepseek-v4.1-flash | releases-8-0-api   |
| opencode/deepseek-v4.1-flash | start-ie11-support |

## Failed runs per case, outside the baseline

| Case                                  | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| ------------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge-dev-run-scheduled-publishing   |                       | 1/5                   |                      | 1/5                    |              |               | 1/5                          |                       |
| info-bulk-redirects                   |                       | 1/5                   |                      |                        |              |               |                              |                       |
| info-find-page-to-edit                |                       | 2/5                   |                      |                        |              |               | 1/5                          |                       |
| info-keyboard-shortcuts               | 3/5                   | 1/5                   | 1/5                  | 1/5                    | 1/5          |               | 2/5                          |                       |
| info-snippets-vs-pages                |                       | 2/5                   |                      |                        | 1/5          |               | 2/5                          | 1/5                   |
| info-stale-pages                      |                       |                       |                      | 1/5                    | 2/5          |               | 3/5                          |                       |
| releases-7-3-to-8-0-overview          |                       | 5/5                   |                      | 1/5                    |              |               | 4/5                          |                       |
| releases-7-4-incomplete-blocks        | 1/5                   | 1/5                   |                      | 1/5                    |              |               |                              |                       |
| releases-8-0-api                      | 1/5                   | 3/5                   |                      |                        |              |               |                              |                       |
| releases-autosave-version             |                       | 1/5                   |                      |                        |              |               |                              |                       |
| start-content-checker                 |                       |                       |                      |                        | 1/5          |               |                              |                       |
| start-restrict-images                 |                       | 1/5                   |                      | 2/5                    |              |               | 1/5                          |                       |
| troubleshoot-changes-not-published    |                       | 1/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-image-upload-rejected    |                       | 1/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-locked-page              | 1/5                   |                       |                      |                        | 3/5          |               | 1/5                          | 3/5                   |
| troubleshoot-no-publish-button        |                       | 2/5                   |                      |                        |              |               |                              | 1/5                   |
| troubleshoot-recover-deleted-document |                       | 4/5                   | 3/5                  | 4/5                    | 5/5          |               | 3/5                          | 1/5                   |
| troubleshoot-scheduled-page-not-live  |                       |                       |                      |                        |              | 1/5           |                              |                       |
| troubleshoot-user-cannot-log-in       |                       | 1/5                   |                      |                        |              |               |                              |                       |
