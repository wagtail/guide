---
name: create-pull-request
description: Steps for creating a pull request in this project.
---

## Requirements

-   GitHub CLI (`gh`) installed and authenticated
    -   `gh pr create` — open the PR creation flow.
    -   `gh pr view` — verify the PR was created correctly.
-   On a feature branch (not main)

## Steps

-   Infer from context or ask the user if this PR fixes or relates to an issue, follow up and ask for the issue number before proceeding.
-   Infer from context or ask the user to describe their AI involvement and review state:
    -   AI generated the code and PR description — has it been reviewed by a human?
    -   AI assisted with the PR description only — has it been reviewed by a human?
    -   Other (ask user to describe) — has it been reviewed by a human?
-   Verify any needed docs and tests changes have been included.
-   Run appropriate quality assurance locally before opening the PR.

## PR title guidance

-   Use a descriptive title that communicates the problem solved or feature added in a few words.
-   Do not use vague titles like "Fixes #123" — write "Fix documentation dark mode refresh issue (#123)" instead.

## Template

-   If fully closes: Fixes #number | If related: Relates to #number
    Fixes/Relates to #

### Description

-   Describe the "why" of the changes. Concisely, why the proposed solution is the right one, and which other solutions might have been skipped.
-   Highlight areas of the proposed changes that require careful review.
-   Guidance on QA done so far vs. testing left to do.

### Testing

-   Only report lint/test results for files included in this PR. Do not mention unrelated or untracked files.
-   Share guidance on any specific tests related to the PR - command(s) and results. Consider if it might be worth to script some of the testing in bash or Python.
-   For frontend changes, add before/after screenshots if possible.
-   Note any manual testing that would be worth doing or areas needing careful review

### AI usage

-   Agent: infer from your context / share user input.
