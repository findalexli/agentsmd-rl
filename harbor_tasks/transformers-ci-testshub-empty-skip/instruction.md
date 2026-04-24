# Bug: `tests_hub` CI job runs on every PR even with no test changes

## Context

The `utils/tests_fetcher.py` module determines which CI test jobs should run for a given PR by matching changed files against regex filters defined in `JOB_TO_TEST_FILE`. It writes per-job test list files (e.g., `tests_torch_test_list.txt`) to an output directory — one file per job that has matching tests. Jobs with no matching tests get no file written, and are thus skipped in CI.

## Problem

The `create_test_list_from_filter()` function has a special case for the `tests_hub` job: instead of filtering via regex like all other jobs, it unconditionally sets `files_to_test = ["tests"]`. This means `tests_hub` always gets a test list file written, causing the CircleCI `tests_hub` job to run on **every single PR commit**, even when no code or test files have actually changed.

Before a recent refactor (PR #30674), this job would not run when no tests were found. The refactor accidentally made `tests_hub` always trigger.

## Expected behavior

When no other CI test jobs have any matching test files (i.e., the PR doesn't touch anything test-relevant), `tests_hub` should also be skipped — an `Empty` job should run instead.

## Relevant code

Look at `create_test_list_from_filter()` in `utils/tests_fetcher.py`, around line 1106. The bug is in how `tests_hub` is handled relative to the other jobs.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
