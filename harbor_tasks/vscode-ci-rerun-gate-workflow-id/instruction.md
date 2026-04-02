# Bug Report: "Rerun Check" button shown for CI checks that cannot be rerun

## Problem

In the CI status widget for GitHub pull requests, the "Rerun Check" action button appears on all failed CI checks, including checks that do not have a valid GitHub Actions workflow run URL. When a user clicks "Rerun" on such a check, the rerun fails because the system cannot extract a workflow run ID from the check's `detailsUrl` — it may be `undefined`, empty, or point to a non-GitHub-Actions URL (e.g., a third-party CI provider).

This results in a confusing user experience where the button is presented but the action silently fails or errors out.

## Expected Behavior

The "Rerun Check" button should only appear on failed CI checks that have a valid, parseable GitHub Actions workflow run URL. Checks without a rerunnable workflow (missing or non-matching `detailsUrl`) should not display the rerun action.

## Actual Behavior

The rerun button is shown for every failed check regardless of whether a workflow run ID can be extracted from its details URL, leading to broken rerun attempts.

## Files to Look At

- `src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts`
- `src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts`
