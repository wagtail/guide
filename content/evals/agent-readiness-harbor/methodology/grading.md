# Grading changes for future evaluations

The case definitions changed on 11 November 2026. These changes apply to newly
prepared evaluations only. Existing results, answers, assertions and grades have
not been regenerated or modified.

## Release question

`start-latest-release` asked for the newest release while its assertions required
8.0. Live retrieval subsequently found 8.1, making the question and grading
expectation disagree. The replacement, `start-release-8-0`, asks about a fixed
release. Its factual check tests the v3 API, which the prompt does not supply;
the semantic rubric checks its content-management capabilities. The citation
check still requires the corresponding guide release-notes page. The task no
longer tests discovery of whichever release is newest.

## Multi-site and multi-tenancy

The previous phrase check rejected a correct table whose heading was
“Database” and whose multi-tenancy cell was “Separate per tenant.” The revised
text check requires the database topic without prescribing adjacent words.
The unchanged semantic rubric still checks shared storage for multi-site,
separate databases for tenants, and the need for customizations. The official
guide citation check and shared nonempty-answer check remain in place.

Both revised cases have `metadata.grading_revision: 2`. There are still 33 cases.
The revision number is descriptive metadata; Harbor's source hash is the
enforced grading identity.

## Comparability and historical replay

Do not pool newly graded runs with the published benchmark as if the questions
and assertions were identical. The release case has a new identifier and task;
the multi-tenancy case keeps its identifier but has a revised factual gate.
Compare matched grading revisions/source hashes, or report these two cases
separately. A source hash does not freeze live website content, model versions
or judge behavior.

`runner.py` records a hash of `tests.yaml`, `default-test.yaml` and every Python
file in the original `graders/` directory when preparing a batch. Its `grade`
command rejects a batch if the current hash differs from the saved manifest.
These edits, including the new regression test file, intentionally change that
hash. Previously prepared batches must not be graded using the new definitions.

To reproduce historical grading, use a separate checkout of the exact original
evaluation source (including the complete grader file set) that matches the
manifest's hash. Do not overwrite the manifest hash or disable the guard.
Historical replay would call the judge again and may produce different judgments;
it is unnecessary for reading existing results and was not performed here.
The trace-analysis pipeline reads saved grades without regrading them.

## Offline verification

Run `just eval-agents-check` for all 33 references, empty/refusal/URL-only answers,
missing citations and prompt leakage. Run the focused regression tests with:

```sh
just --command uv run python -m unittest discover \
  -s content/evals/agent-readiness/graders -p 'test_check_cases.py'
```

These checks exercise deterministic assertions only; they do not validate or
call the semantic judge.
