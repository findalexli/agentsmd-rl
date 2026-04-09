# Fix: Make Mergeable Check Green for Revert PRs

## Problem

When creating a revert PR in ClickHouse, the `Mergeable Check` stays red even when the only required check (`Fast test`) passes. This makes it harder than necessary to merge urgent revert PRs, which should be as easy as possible to incentivize quick reverts.

## Your Task

Modify `ci/praktika/native_jobs.py` to detect revert PRs and make the mergeable check green when:
1. The PR body contains "Reverts ClickHouse/" (indicating it's a revert PR)
2. The `Fast test` has NOT failed
3. Even if other jobs have failed

## Context

The relevant code is in the `_finish_workflow` function in `ci/praktika/native_jobs.py`. Look for where `failed_results` and `ready_for_merge_status` are handled.

The function currently:
1. Collects failed job results into `failed_results` list
2. Sets `ready_for_merge_status = Result.Status.FAILED` if there are any failures
3. Posts the commit status via `GH.post_commit_status()`

You need to add logic between the failure processing and the status posting that:
- Checks if PR body contains "Reverts ClickHouse/"
- Checks if any failed result contains "Fast test"
- If it's a revert PR AND Fast test hasn't failed, override the status to SUCCESS

## Expected Behavior

After your fix, when a revert PR is created:
- If `Fast test` passes but other jobs fail, the mergeable check should be green
- The description should indicate it's a revert PR
- A log message should be printed indicating the revert PR was detected

## Notes

- The `env` object has a `PR_BODY` attribute containing the PR description
- `Result.Status.SUCCESS` is the success status constant
- The fix should be a small conditional block added in the appropriate location
