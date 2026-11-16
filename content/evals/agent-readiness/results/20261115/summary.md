## Results per arm, 5 repeat(s) (mean ± SD across repeats)

| Arm                          | Runs | Pass    | Facts | Citation | Judge | Cost/answer | Duration | Tool calls |
| ---------------------------- | ---- | ------- | ----- | -------- | ----- | ----------- | -------- | ---------- |
| claude-code/fable-5.2        | 165  | 98% ± 3 | 100%  | 98%      | 100%  | 21.1¢       | 29s      | 5.2        |
| claude-code/haiku-5.5        | 165  | 83% ± 5 | 98%   | 89%      | 94%   | 1.6¢        | 29s      | 3.6        |
| claude-code/opus-5.5         | 165  | 96% ± 3 | 99%   | 98%      | 99%   | 10.0¢       | 29s      | 4.6        |
| claude-code/sonnet-5.5       | 165  | 96% ± 3 | 100%  | 97%      | 99%   | 5.0¢        | 27s      | 4.8        |
| codex/luna-6                 | 165  | 92% ± 3 | 98%   | 93%      | 98%   | 0.3¢        | 13s      | 1.9        |
| codex/sol-6.1                | 165  | 99% ± 2 | 100%  | 99%      | 100%  | 5.2¢        | 11s      | 1.4        |
| opencode/deepseek-v4.1-flash | 165  | 82% ± 0 | 93%   | 85%      | 88%   | 0.0¢        | 19s      | 2.4        |
| opencode/qwen-3.8-27b        | 165  | 96% ± 4 | 99%   | 98%      | 97%   | 1.1¢        | 45s      | 3.7        |

## Median of 5 runs per case

| Arm                          | Cases passed | Median duration | Suite duration | Median cost | Suite cost |
| ---------------------------- | ------------ | --------------- | -------------- | ----------- | ---------- |
| claude-code/fable-5.2        | 33/33        | 29s             | 15.4 min       | 20.68¢      | $6.94      |
| claude-code/haiku-5.5        | 27/33        | 27s             | 14.9 min       | 1.52¢       | $0.51      |
| claude-code/opus-5.5         | 33/33        | 26s             | 15.7 min       | 9.52¢       | $3.26      |
| claude-code/sonnet-5.5       | 32/33        | 25s             | 14.0 min       | 4.77¢       | $1.62      |
| codex/luna-6                 | 31/33        | 10s             | 6.6 min        | 0.29¢       | $0.11      |
| codex/sol-6.1                | 33/33        | 11s             | 5.9 min        | 4.78¢       | $1.71      |
| opencode/deepseek-v4.1-flash | 28/33        | 14s             | 8.5 min        | -           | -          |
| opencode/qwen-3.8-27b        | 33/33        | 34s             | 22.1 min       | 0.78¢       | $0.32      |

## Pass rate by task

| Task            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge          | 100%                  | 60%                   | 100%                 | 100%                   | 100%         | 100%          | 60%                          | 100%                  |
| information     | 97%                   | 91%                   | 99%                  | 97%                    | 96%          | 100%          | 81%                          | 95%                   |
| negative        | 100%                  | 100%                  | 100%                 | 100%                   | 100%         | 100%          | 100%                         | 100%                  |
| releases        | 100%                  | 80%                   | 97%                  | 100%                   | 100%         | 100%          | 80%                          | 100%                  |
| troubleshooting | 95%                   | 68%                   | 88%                  | 88%                    | 72%          | 95%           | 80%                          | 95%                   |

## Pass rate by framing

| Framing        | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| -------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| site-named     | 100%                  | 87%                   | 98%                  | 100%                   | 98%          | 98%           | 88%                          | 97%                   |
| site-not-named | 91%                   | 69%                   | 89%                  | 87%                    | 73%          | 100%          | 60%                          | 93%                   |
| site-start     | 100%                  | 92%                   | 100%                 | 96%                    | 100%         | 100%          | 96%                          | 100%                  |

## Surfaces reached (share of runs; counts are per run)

| Column                            | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| --------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| web_search_used                   | 0%                    | 75%                   | 6%                   | 8%                     | 97%          | 98%           | 30%                          | 76%                   |
| homepage_reached                  | 9%                    | 23%                   | 10%                  | 45%                    | 3%           | 4%            | 27%                          | 28%                   |
| docs_reached                      | 84%                   | 60%                   | 82%                  | 76%                    | 9%           | 29%           | 53%                          | 62%                   |
| markdown_page_reached             | 19%                   | 9%                    | 19%                  | 40%                    | 0%           | 0%            | 32%                          | 15%                   |
| llms_txt_reached                  | 44%                   | 15%                   | 36%                  | 56%                    | 0%           | 0%            | 32%                          | 16%                   |
| llms_full_reached                 | 2%                    | 0%                    | 2%                   | 1%                     | 0%           | 0%            | 1%                           | 1%                    |
| skill_reached                     | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 1%                    |
| mcp_used                          | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| sitemap_reached                   | 4%                    | 1%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 1%                    |
| robots_txt_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| well_known_reached                | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| openapi_reached                   | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| dev_docs_reached                  | 14%                   | 14%                   | 13%                  | 8%                     | 2%           | 1%            | 7%                           | 21%                   |
| github_copy_reached               | 0%                    | 0%                    | 0%                   | 0%                     | 0%           | 0%            | 0%                           | 0%                    |
| external_reached                  | 0%                    | 1%                    | 1%                   | 1%                     | 1%           | 0%            | 1%                           | 2%                    |
| answer_cites_guide                | 88%                   | 81%                   | 89%                  | 87%                    | 81%          | 88%           | 76%                          | 87%                   |
| answer_grounded                   | 87%                   | 59%                   | 81%                  | 78%                    | 5%           | 23%           | 41%                          | 55%                   |
| citations_not_fetched             | 0.1                   | 0.5                   | 0.2                  | 0.4                    | 1.2          | 1.2           | 0.5                          | 0.5                   |
| versioned_url_reached             | 84%                   | 9%                    | 80%                  | 36%                    | 0%           | 0%            | 30%                          | 0%                    |
| answer_cites_versioned_url        | 42%                   | 18%                   | 45%                  | 10%                    | 0%           | 0%            | 2%                           | 0%                    |
| legacy_editor_manual_reached      | 2%                    | 1%                    | 1%                   | 6%                     | 1%           | 0%            | 1%                           | 1%                    |
| answer_cites_legacy_editor_manual | 0%                    | 6%                    | 1%                   | 2%                     | 5%           | 0%            | 1%                           | 0%                    |
| fetch_errors                      | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.3                          | 0.8                   |
| curl_calls                        | 0.0                   | 0.0                   | 0.0                  | 0.1                    | 0.0          | 0.0           | 0.1                          | 0.0                   |
| permission_denials                | 0.0                   | 0.0                   | 0.0                  | 0.0                    | 0.0          | 0.0           | 0.0                          | 0.0                   |

## Judge couldn't tell (passed as UNKNOWN, review by hand)

| Arm                          | Case                               |
| ---------------------------- | ---------------------------------- |
| claude-code/haiku-5.5        | info-stale-pages                   |
| claude-code/haiku-5.5        | info-stale-pages                   |
| claude-code/haiku-5.5        | troubleshoot-locked-page           |
| codex/sol-6.1                | releases-autosave-version          |
| opencode/qwen-3.8-27b        | info-stale-pages                   |
| opencode/deepseek-v4.1-flash | troubleshoot-image-upload-rejected |
| opencode/qwen-3.8-27b        | releases-8-0-api                   |
| opencode/deepseek-v4.1-flash | releases-7-4-incomplete-blocks     |

## Failed runs per case, outside the baseline

| Case                                  | claude-code/fable-5.2 | claude-code/haiku-5.5 | claude-code/opus-5.5 | claude-code/sonnet-5.5 | codex/luna-6 | codex/sol-6.1 | opencode/deepseek-v4.1-flash | opencode/qwen-3.8-27b |
| ------------------------------------- | --------------------- | --------------------- | -------------------- | ---------------------- | ------------ | ------------- | ---------------------------- | --------------------- |
| bridge-dev-run-scheduled-publishing   |                       | 2/5                   |                      |                        |              |               | 2/5                          |                       |
| info-find-page-to-edit                |                       |                       |                      |                        | 1/5          |               |                              | 1/5                   |
| info-image-focal-area                 |                       | 1/5                   |                      |                        |              |               |                              |                       |
| info-keyboard-shortcuts               | 2/5                   | 1/5                   | 1/5                  |                        | 1/5          |               | 3/5                          |                       |
| info-moderator-vs-editor              |                       |                       |                      |                        |              |               | 3/5                          |                       |
| info-multi-site-vs-multi-tenancy      |                       |                       |                      |                        |              |               | 1/5                          | 1/5                   |
| info-private-page                     |                       |                       |                      |                        |              |               |                              | 1/5                   |
| info-snippets-vs-pages                |                       | 3/5                   |                      |                        |              |               | 1/5                          |                       |
| info-stale-pages                      |                       | 1/5                   |                      | 1/5                    | 1/5          |               | 5/5                          | 1/5                   |
| releases-7-3-to-8-0-overview          |                       | 5/5                   |                      |                        |              |               | 4/5                          |                       |
| releases-7-4-incomplete-blocks        |                       |                       | 1/5                  |                        |              |               | 1/5                          |                       |
| releases-8-0-image-formats            |                       |                       |                      |                        |              |               | 1/5                          |                       |
| start-release-8-0                     |                       | 1/5                   |                      |                        |              |               |                              |                       |
| start-restrict-images                 |                       | 1/5                   |                      | 1/5                    |              |               | 1/5                          |                       |
| troubleshoot-changes-not-published    |                       |                       | 1/5                  |                        |              |               |                              |                       |
| troubleshoot-image-upload-rejected    |                       | 3/5                   |                      |                        |              |               | 1/5                          |                       |
| troubleshoot-locked-page              | 1/5                   | 3/5                   | 2/5                  | 1/5                    | 5/5          |               | 2/5                          | 2/5                   |
| troubleshoot-no-publish-button        |                       | 3/5                   |                      |                        |              |               |                              |                       |
| troubleshoot-recover-deleted-document | 1/5                   | 4/5                   | 2/5                  | 4/5                    | 5/5          |               | 5/5                          |                       |
| troubleshoot-scheduled-page-not-live  |                       |                       |                      |                        | 1/5          | 2/5           |                              |                       |
