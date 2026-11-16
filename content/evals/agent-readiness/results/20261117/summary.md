## Results per arm, 5 repeat(s) (mean ± SD across repeats)

| Arm                          | Runs | Pass    | Facts | Citation | Judge | Cost/answer | Duration | Tool calls |
| ---------------------------- | ---- | ------- | ----- | -------- | ----- | ----------- | -------- | ---------- |
| claude-code/fable-5.2        | 165  | 99% ± 1 | 100%  | 99%      | 100%  | 20.8¢       | 25s      | 4.0        |
| claude-code/haiku-5.5        | 165  | 81% ± 3 | 98%   | 89%      | 92%   | 1.7¢        | 26s      | 3.3        |
| claude-code/opus-5.5         | 165  | 96% ± 3 | 100%  | 98%      | 100%  | 10.0¢       | 27s      | 3.7        |
| claude-code/sonnet-5.5       | 165  | 95% ± 3 | 99%   | 96%      | 99%   | 4.9¢        | 22s      | 3.9        |
| codex/luna-6                 | 165  | 91% ± 4 | 99%   | 92%      | 97%   | 0.4¢        | 12s      | 2.1        |
| codex/sol-6.1                | 165  | 99% ± 2 | 100%  | 99%      | 100%  | 5.2¢        | 10s      | 1.3        |
| opencode/deepseek-v4.1-flash | 165  | 86% ± 6 | 93%   | 88%      | 91%   | 0.0¢        | 11s      | 2.4        |
| opencode/qwen-3.8-27b        | 165  | 95% ± 3 | 99%   | 95%      | 98%   | 1.1¢        | 39s      | 3.3        |

## Median of 5 runs per case

| Arm                          | Cases passed | Median duration | Suite duration | Median cost | Suite cost |
| ---------------------------- | ------------ | --------------- | -------------- | ----------- | ---------- |
| claude-code/fable-5.2        | 33/33        | 25s             | 13.5 min       | 20.43¢      | $6.86      |
| claude-code/haiku-5.5        | 27/33        | 28s             | 14.4 min       | 1.66¢       | $0.54      |
| claude-code/opus-5.5         | 32/33        | 25s             | 14.2 min       | 9.66¢       | $3.25      |
| claude-code/sonnet-5.5       | 32/33        | 22s             | 11.8 min       | 4.76¢       | $1.60      |
| codex/luna-6                 | 31/33        | 9s              | 6.5 min        | 0.29¢       | $0.11      |
| codex/sol-6.1                | 33/33        | 9s              | 5.6 min        | 4.84¢       | $1.72      |
| opencode/deepseek-v4.1-flash | 30/33        | 9s              | 5.0 min        | -           | -          |
| opencode/qwen-3.8-27b        | 33/33        | 34s             | 20.5 min       | 0.94¢       | $0.33      |

## Pass rate by task

| Task            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge          | 100%                  | 80%                   | 60%                  | 100%                   | 100%         | 100%          | 60%                          | 100%                  |
| information     | 100%                  | 88%                   | 97%                  | 97%                    | 93%          | 100%          | 88%                          | 95%                   |
| negative        | 100%                  | 100%                  | 100%                 | 100%                   | 100%         | 100%          | 100%                         | 100%                  |
| releases        | 100%                  | 80%                   | 100%                 | 100%                   | 93%          | 100%          | 100%                         | 93%                   |
| troubleshooting | 98%                   | 62%                   | 92%                  | 82%                    | 80%          | 95%           | 70%                          | 95%                   |

## Pass rate by framing

| Framing        | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| -------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| site-named     | 100%                  | 83%                   | 100%                 | 100%                   | 97%          | 98%           | 94%                          | 98%                   |
| site-not-named | 98%                   | 69%                   | 84%                  | 82%                    | 76%          | 100%          | 64%                          | 87%                   |
| site-start     | 100%                  | 96%                   | 100%                 | 96%                    | 96%          | 100%          | 96%                          | 100%                  |

## Surfaces reached (share of runs; counts are per run)

| Column                            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| web_search_used                   | 1%                    | 76%                   | 4%                   | 7%                     | 97%          | 97%           | 30%                          | 81%                   |
| homepage_reached                  | 7%                    | 19%                   | 6%                   | 50%                    | 3%           | 3%            | 27%                          | 16%                   |
| docs_reached                      | 84%                   | 62%                   | 84%                  | 77%                    | 11%          | 30%           | 51%                          | 59%                   |
| markdown_page_reached             | 0%                    | 3%                    | 1%                   | 4%                     | 0%           | 0%            | 12%                          | 2%                    |
| llms_txt_reached                  | 0%                    | 1%                    | 0%                   | 1%                     | 0%           | 0%            | 2%                           | 1%                    |
| llms_full_reached                 | 0%                    | 1%                    | 0%                   | 0%                     | 0%           | 0%            | 1%                           | 0%                    |
| skill_reached                     | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| mcp_used                          | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| sitemap_reached                   | 4%                    | 2%                    | 0%                   | 0%                     | 0%           | 0%            | 1%                           | 1%                    |
| robots_txt_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 1%                           | 0%                    |
| well_known_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| openapi_reached                   | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| dev_docs_reached                  | 12%                   | 18%                   | 13%                  | 15%                    | 5%           | 0%            | 9%                           | 17%                   |
| github_copy_reached               | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| external_reached                  | 0%                    | 0%                    | 2%                   | 0%                     | 0%           | 0%            | 1%                           | 1%                    |
| answer_cites_guide                | 88%                   | 81%                   | 88%                  | 87%                    | 82%          | 88%           | 79%                          | 84%                   |
| answer_grounded                   | 86%                   | 63%                   | 82%                  | 78%                    | 6%           | 27%           | 41%                          | 53%                   |
| citations_not_fetched             | 0.1                   | 0.4                   | 0.2                  | 0.4                    | 1.2          | 1.2           | 0.6                          | 0.5                   |
| versioned_url_reached             | 84%                   | 10%                   | 80%                  | 33%                    | 1%           | 0%            | 28%                          | 0%                    |
| answer_cites_versioned_url        | 36%                   | 17%                   | 37%                  | 14%                    | 0%           | 0%            | 2%                           | 0%                    |
| legacy_editor_manual_reached      | 2%                    | 1%                    | 4%                   | 9%                     | 4%           | 0%            | 1%                           | 2%                    |
| answer_cites_legacy_editor_manual | 0%                    | 7%                    | 2%                   | 2%                     | 5%           | 0%            | 0%                           | 0%                    |
| fetch_errors                      | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.3                          | 0.7                   |
| curl_calls                        | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.2                          | 0.1                   |
| permission_denials                | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.0                          | 0.0                   |

## Judge couldn't tell (passed as UNKNOWN, review by hand)

| Arm                          | Case                           |
| ---------------------------- | ------------------------------ |
| codex/luna-6                 | troubleshoot-locked-page       |
| codex/sol-6.1                | releases-autosave-version      |
| codex/sol-6.1                | releases-7-3-to-8-0-overview   |
| opencode/deepseek-v4.1-flash | troubleshoot-no-publish-button |

## Failed runs per case, outside the baseline

| Case                                  | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| ------------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge-dev-run-scheduled-publishing   |                       | 1/5                   | 2/5                  |                        |              |               | 2/5                          |                       |
| info-copy-vs-alias                    |                       | 1/5                   |                      |                        |              |               |                              |                       |
| info-find-page-to-edit                |                       | 1/5                   |                      |                        |              |               |                              |                       |
| info-keyboard-shortcuts               |                       |                       | 2/5                  | 1/5                    | 1/5          |               |                              | 1/5                   |
| info-multi-site-vs-multi-tenancy      |                       |                       |                      |                        |              |               | 1/5                          |                       |
| info-private-page                     |                       |                       |                      |                        |              |               | 1/5                          |                       |
| info-snippets-vs-pages                |                       | 4/5                   |                      |                        | 2/5          |               | 1/5                          | 2/5                   |
| info-stale-pages                      |                       | 2/5                   |                      |                        | 1/5          |               | 5/5                          | 1/5                   |
| releases-7-3-to-8-0-overview          |                       | 5/5                   |                      |                        | 1/5          |               |                              | 1/5                   |
| releases-7-4-incomplete-blocks        |                       |                       |                      |                        | 1/5          |               |                              |                       |
| releases-8-0-api                      |                       | 1/5                   |                      |                        |              |               |                              |                       |
| releases-8-0-image-formats            |                       |                       |                      |                        |              |               |                              | 1/5                   |
| start-content-checker                 |                       |                       |                      |                        |              |               | 1/5                          |                       |
| start-restrict-images                 |                       | 1/5                   |                      | 1/5                    | 1/5          |               |                              |                       |
| troubleshoot-changes-not-published    |                       |                       |                      |                        |              |               | 2/5                          |                       |
| troubleshoot-image-upload-rejected    |                       | 3/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-locked-page              |                       | 4/5                   |                      | 2/5                    | 3/5          |               | 4/5                          | 2/5                   |
| troubleshoot-no-publish-button        |                       | 4/5                   |                      |                        |              |               | 2/5                          |                       |
| troubleshoot-recover-deleted-document | 1/5                   | 3/5                   | 3/5                  | 5/5                    | 4/5          |               | 4/5                          |                       |
| troubleshoot-scheduled-page-not-live  |                       |                       |                      |                        | 1/5          | 2/5           |                              |                       |
| troubleshoot-user-cannot-log-in       |                       | 1/5                   |                      |                        |              |               |                              |                       |
