---
name: create-pull-request
description: Steps for creating a pull request in this project.
---

## Requirements

-   GitHub CLI (`gh`) installed and authenticated
-   On a feature branch (not main)

## Steps

-   Ask the user if this PR fixes or relates to an issue, follow up and ask for the issue number before proceeding.
-   Ask the user to describe their AI involvement and review state:
    -   AI generated the code and PR description — has it been reviewed by a human?
    -   AI assisted with the PR description only — has it been reviewed by a human?
    -   Other (ask user to describe) — has it been reviewed by a human?
-   Verify any needed docs and tests changes have been included.
-   Run `make format`, `make lint`, and `make test` before opening the PR.
-   For frontend changes, remind the human to add before/after screenshots.

## PR title guidance

-   Use a descriptive title that communicates the problem solved or feature added in a few words.
-   Do not use vague titles like "Fixes #123" — write "Fix documentation dark mode refresh issue" instead.

## Template

-   If fully closes: Fixes #number | If related: Relates to #number
    Fixes/Relates to #

### Description

-   Describe the "why" of the changes, why the proposed solution is the right one.
-   Highlight areas of the proposed changes that require careful review.
-   Guidance on QA done so far vs. testing left to do.

### Testing

-   Summarise results briefly, e.g. "All tests pass, no lint errors"
-   Note any testing still left to do or areas needing careful review
-   relevant test evidence (command + result)
-   Only report lint/test results for files included in this PR. Do not mention unrelated or untracked files.

### AI usage

-   Agent: paste the user's answer here

## Commands

-   `gh pr create` — open the PR creation flow.
-   `gh pr view` — verify the PR was created correctly.
