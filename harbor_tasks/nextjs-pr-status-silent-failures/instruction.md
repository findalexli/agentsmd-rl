# Fix pr-status.js: silent failure reporting bugs

## Problem

When running `node scripts/pr-status.js <PR_NUMBER>`, the script sometimes reports "No failed jobs found" even when the PR has actual CI failures. Two separate issues contribute to this:

1. **API errors are silently swallowed.** When the GitHub API returns a transient error during job pagination, the script catches the error and breaks out of the loop, returning an empty result set. This causes all downstream analysis to report zero failures.

2. **Some failure types are invisible.** GitHub Actions uses several distinct `conclusion` values for failed jobs — not just `"failure"`. Jobs that timed out or had runner startup failures are silently omitted from all reports and analysis, including the flaky test detection.

## Expected Behavior

- When API calls fail during job fetching, the script should retry before giving up. If all retries fail on the first page, it should throw an error rather than silently returning empty results.
- All relevant GitHub Actions failure conclusions should be detected and reported across all parts of the script: job filtering, job categorization, report generation, and flaky test detection.
- The report table should clearly indicate when a job's conclusion type differs from a standard failure.

## Script Requirements

The script at `scripts/pr-status.js` must maintain the following structural elements:

**Helper functions** that must be present:
- `function exec(` — shell command executor
- `function execAsync(` — async shell command executor
- `function execJson(` — JSON-parsing command executor
- `formatDuration`, `formatElapsedTime`, `sanitizeFilename`, `escapeMarkdownTableCell`, `stripTimestamps`

**Main entry point**:
- `async function main(` — the main async function
- `module.exports` — the script must export functions for use by other modules

**Code quality**:
- The script must pass `prettier --check scripts/pr-status.js` formatting
- No use of `eval()` (security)
- Must use `child_process` module for shell commands

## Files to Look At

- `scripts/pr-status.js` — The CI analysis script. Key areas: job fetching/pagination, job filtering, job categorization, report generation, and flaky test detection.