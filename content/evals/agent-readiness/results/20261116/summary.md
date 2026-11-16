## Results per arm, 5 repeat(s) (mean ± SD across repeats)

| Arm                          | Runs | Pass    | Facts | Citation | Judge | Cost/answer | Duration | Tool calls |
| ---------------------------- | ---- | ------- | ----- | -------- | ----- | ----------- | -------- | ---------- |
| claude-code/fable-5.2        | 165  | 96% ± 2 | 99%   | 96%      | 99%   | 21.2¢       | 28s      | 4.7        |
| claude-code/haiku-5.5        | 165  | 82% ± 4 | 98%   | 89%      | 93%   | 1.6¢        | 27s      | 3.5        |
| claude-code/opus-5.5         | 165  | 95% ± 6 | 98%   | 98%      | 99%   | 10.1¢       | 28s      | 4.3        |
| claude-code/sonnet-5.5       | 165  | 95% ± 3 | 98%   | 95%      | 97%   | 5.0¢        | 25s      | 4.6        |
| codex/luna-6                 | 165  | 92% ± 4 | 97%   | 93%      | 97%   | 0.4¢        | 13s      | 2.0        |
| codex/sol-6.1                | 165  | 98% ± 1 | 100%  | 98%      | 100%  | 5.2¢        | 11s      | 1.4        |
| opencode/deepseek-v4.1-flash | 165  | 87% ± 3 | 93%   | 89%      | 94%   | 0.0¢        | 14s      | 2.3        |
| opencode/qwen-3.8-27b        | 165  | 94% ± 4 | 99%   | 94%      | 99%   | 1.1¢        | 43s      | 3.5        |

## Median of 5 runs per case

| Arm                          | Cases passed | Median duration | Suite duration | Median cost | Suite cost |
| ---------------------------- | ------------ | --------------- | -------------- | ----------- | ---------- |
| claude-code/fable-5.2        | 32/33        | 26s             | 14.6 min       | 20.57¢      | $6.96      |
| claude-code/haiku-5.5        | 30/33        | 25s             | 14.5 min       | 1.67¢       | $0.53      |
| claude-code/opus-5.5         | 33/33        | 25s             | 14.7 min       | 9.65¢       | $3.26      |
| claude-code/sonnet-5.5       | 31/33        | 23s             | 13.3 min       | 4.89¢       | $1.61      |
| codex/luna-6                 | 31/33        | 10s             | 6.6 min        | 0.28¢       | $0.12      |
| codex/sol-6.1                | 32/33        | 10s             | 5.9 min        | 4.78¢       | $1.72      |
| opencode/deepseek-v4.1-flash | 28/33        | 12s             | 7.0 min        | -           | -          |
| opencode/qwen-3.8-27b        | 32/33        | 33s             | 21.9 min       | 0.82¢       | $0.32      |

## Pass rate by task

| Task            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge          | 100%                  | 60%                   | 80%                  | 100%                   | 100%         | 100%          | 100%                         | 100%                  |
| information     | 97%                   | 87%                   | 97%                  | 99%                    | 97%          | 100%          | 88%                          | 93%                   |
| negative        | 100%                  | 100%                  | 100%                 | 100%                   | 100%         | 100%          | 100%                         | 100%                  |
| releases        | 93%                   | 80%                   | 93%                  | 90%                    | 97%          | 100%          | 90%                          | 93%                   |
| troubleshooting | 92%                   | 70%                   | 92%                  | 88%                    | 75%          | 90%           | 78%                          | 92%                   |

## Pass rate by framing

| Framing        | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| -------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| site-named     | 98%                   | 83%                   | 98%                  | 97%                    | 98%          | 96%           | 96%                          | 99%                   |
| site-not-named | 89%                   | 73%                   | 87%                  | 87%                    | 76%          | 100%          | 62%                          | 82%                   |
| site-start     | 100%                  | 92%                   | 100%                 | 100%                   | 100%         | 100%          | 100%                         | 96%                   |

## Surfaces reached (share of runs; counts are per run)

| Column                            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| web_search_used                   | 1%                    | 72%                   | 5%                   | 7%                     | 97%          | 97%           | 30%                          | 78%                   |
| homepage_reached                  | 10%                   | 23%                   | 9%                   | 46%                    | 4%           | 4%            | 23%                          | 18%                   |
| docs_reached                      | 85%                   | 65%                   | 84%                  | 79%                    | 8%           | 28%           | 53%                          | 61%                   |
| markdown_page_reached             | 3%                    | 8%                    | 2%                   | 21%                    | 0%           | 0%            | 11%                          | 3%                    |
| llms_txt_reached                  | 8%                    | 12%                   | 9%                   | 27%                    | 0%           | 0%            | 13%                          | 2%                    |
| llms_full_reached                 | 1%                    | 0%                    | 0%                   | 1%                     | 0%           | 0%            | 1%                           | 1%                    |
| skill_reached                     | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| mcp_used                          | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| sitemap_reached                   | 4%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 1%                    |
| robots_txt_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| well_known_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| openapi_reached                   | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| dev_docs_reached                  | 16%                   | 13%                   | 14%                  | 13%                    | 2%           | 1%            | 9%                           | 20%                   |
| github_copy_reached               | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| external_reached                  | 1%                    | 0%                    | 1%                   | 0%                     | 1%           | 0%            | 1%                           | 2%                    |
| answer_cites_guide                | 87%                   | 82%                   | 90%                  | 88%                    | 81%          | 89%           | 79%                          | 84%                   |
| answer_grounded                   | 85%                   | 64%                   | 84%                  | 79%                    | 5%           | 25%           | 39%                          | 50%                   |
| citations_not_fetched             | 0.1                   | 0.4                   | 0.1                  | 0.3                    | 1.3          | 1.2           | 0.6                          | 0.5                   |
| versioned_url_reached             | 84%                   | 8%                    | 82%                  | 36%                    | 1%           | 0%            | 30%                          | 0%                    |
| answer_cites_versioned_url        | 40%                   | 14%                   | 49%                  | 18%                    | 0%           | 0%            | 2%                           | 0%                    |
| legacy_editor_manual_reached      | 2%                    | 1%                    | 2%                   | 8%                     | 1%           | 0%            | 1%                           | 0%                    |
| answer_cites_legacy_editor_manual | 0%                    | 5%                    | 2%                   | 1%                     | 4%           | 0%            | 1%                           | 0%                    |
| fetch_errors                      | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.3                          | 0.8                   |
| curl_calls                        | 0.0                   | 0.0                   | 0.0                  | 0.1                    | 0.0          | 0.0           | 0.0                          | 0.0                   |
| permission_denials                | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.0                          | 0.0                   |

## Judge couldn't tell (passed as UNKNOWN, review by hand)

| Arm                   | Case                         |
| --------------------- | ---------------------------- |
| claude-code/haiku-5.5 | start-restrict-images        |
| codex/luna-6          | releases-8-0-api             |
| codex/luna-6          | releases-7-3-to-8-0-overview |

## Failed runs per case, outside the baseline

| Case                                  | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| ------------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge-dev-run-scheduled-publishing   |                       | 2/5                   | 1/5                  |                        |              |               |                              |                       |
| info-bulk-redirects                   |                       | 2/5                   |                      |                        |              |               |                              |                       |
| info-find-page-to-edit                |                       | 2/5                   |                      |                        |              |               |                              |                       |
| info-keyboard-shortcuts               | 2/5                   | 1/5                   | 2/5                  |                        | 1/5          |               | 1/5                          |                       |
| info-snippets-vs-pages                |                       | 2/5                   |                      |                        |              |               | 3/5                          | 4/5                   |
| info-stale-pages                      |                       | 1/5                   |                      | 1/5                    | 1/5          |               | 5/5                          | 1/5                   |
| releases-7-3-to-8-0-overview          |                       | 5/5                   |                      |                        |              |               | 3/5                          | 1/5                   |
| releases-7-4-incomplete-blocks        | 2/5                   |                       | 2/5                  | 3/5                    |              |               |                              |                       |
| releases-8-0-api                      |                       | 1/5                   |                      |                        | 1/5          |               |                              |                       |
| start-release-8-0                     |                       |                       |                      |                        |              |               |                              | 1/5                   |
| start-restrict-images                 |                       | 2/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-concurrent-editing       |                       |                       |                      |                        |              |               | 1/5                          |                       |
| troubleshoot-image-upload-rejected    |                       | 2/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-locked-page              | 3/5                   | 1/5                   | 1/5                  | 1/5                    | 4/5          |               | 3/5                          | 2/5                   |
| troubleshoot-no-publish-button        |                       | 4/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-recover-deleted-document |                       | 5/5                   | 2/5                  | 4/5                    | 5/5          |               | 5/5                          | 1/5                   |
| troubleshoot-scheduled-page-not-live  |                       |                       |                      |                        | 1/5          | 4/5           |                              |                       |
