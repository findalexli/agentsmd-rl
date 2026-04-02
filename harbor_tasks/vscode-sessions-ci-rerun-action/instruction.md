# Bug Report: No way to rerun failed CI checks from the Sessions CI status widget

## Problem

When viewing CI check results in the Sessions CI status widget, failed checks are displayed but there is no action available to rerun them. Developers who encounter a flaky or transient CI failure must leave VS Code and navigate to GitHub's web UI to manually trigger a rerun of failed jobs. This breaks the workflow for users who rely on the Sessions panel to manage their pull request lifecycle entirely within the editor.

## Expected Behavior

Failed CI checks in the CI status widget should offer a "Rerun Check" action (similar to the existing "Open on GitHub" action) that triggers a rerun of the failed jobs via the GitHub Actions API, then refreshes the CI status automatically.

## Actual Behavior

Failed CI checks only show a link to open the check on GitHub. There is no inline rerun action, no API integration for rerunning failed jobs, and no logic to extract the workflow run ID from a check's details URL.

## Files to Look At

- `src/vs/sessions/contrib/changes/browser/ciStatusWidget.ts`
- `src/vs/sessions/contrib/github/browser/fetchers/githubPRCIFetcher.ts`
- `src/vs/sessions/contrib/github/browser/models/githubPullRequestCIModel.ts`
