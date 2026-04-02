# Bug: Concurrent `/rerun-ut` slash commands post duplicate workflow URLs

## Summary

When multiple `/rerun-ut` commands are issued in quick succession on a pull request (e.g., to rerun different test files), the bot posts the **same** workflow run URL for all of them. Additionally, each `/rerun-ut` command posts **two separate comments** (one for the trigger status and one for the workflow URL), making the comment thread noisy.

## Reproduction

1. On a PR, post two `/rerun-ut` commands back-to-back, each targeting a different test file.
2. Observe that both commands link to the same workflow run URL, even though they dispatched separate workflows.
3. Notice that each command produces two comments instead of one consolidated comment.

## Root Cause

The function that polls for the workflow run URL after dispatch (`find_workflow_run_url` in `scripts/ci/utils/slash_command_handler.py`) identifies runs by matching the `display_title` field. The workflow's `run-name` in `.github/workflows/rerun-ut.yml` does **not** include any per-dispatch distinguishing information (like the test command being run), so all `/rerun-ut` dispatches produce runs with an identical display title. The polling function therefore matches the first run it finds, regardless of which dispatch it belongs to.

The same handler function (`handle_rerun_ut`) also posts the trigger confirmation and the workflow URL as two separate PR comments, which is unnecessarily verbose.

## Affected Files

- `.github/workflows/rerun-ut.yml` — the workflow `run-name` template
- `scripts/ci/utils/slash_command_handler.py` — the `find_workflow_run_url` function and the `/rerun-ut` handler (`handle_rerun_ut`)

## Expected Behavior

- Each `/rerun-ut` dispatch should be matchable to its own unique workflow run, even when multiple dispatches happen concurrently.
- The bot should post a single consolidated comment per `/rerun-ut` command (combining the trigger status and the workflow URL).
- The `/rerun-stage` handler should also consolidate its comments in the same way.
