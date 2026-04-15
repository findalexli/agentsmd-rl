# Fix Release Script Robustness Issues

The `scripts/create-github-release.mjs` script has several fragility issues that need to be fixed to make the release process more robust.

## Issues to Fix

### 1. Fragile Git Commit Range Detection

The current script uses a `git log` command with `-n 1` and `HEAD~1` to find the previous release commit. This is fragile because it limits results to a single commit and relies on a relative reference that doesn't reliably identify the actual previous release commit.

The script should instead retrieve **all** commits matching the "ci: changeset release" pattern (not limited to one), parse the output into an array by splitting on newlines and removing empty entries, and use the first two entries to identify the current and previous release commits. The git log range should be constructed from these identified commits rather than from `HEAD~1`. If only one release commit exists, the range should fall back to one commit before the current release.

Since the script runs immediately after the "ci: changeset release" commit is pushed, HEAD is always the current release commit. The goal is to get commits between the previous release and the current one, excluding both release commits themselves.

### 2. Brittle Non-Conventional Commit Parsing

The script's handling of non-conventional commits (merge commits, etc.) uses manual index tracking with double `indexOf(' ')` calls and string slicing to extract the hash, email, and subject fields. This approach is brittle and hard to follow.

It should be replaced with a cleaner approach: split each log line on spaces and extract the hash from the first element, the email from the second element, and the subject from the remaining elements joined back together with spaces. The `scope` field should remain `null` for non-conventional commits.

### 3. Incorrect --latest Flag Handling

The `--latest` flag is always passed unconditionally to `gh release create`, but it should only apply to non-prerelease releases. The existing `prereleaseFlag` variable already handles the `--prerelease` flag conditionally — the `--latest` flag needs similar conditional treatment, where it is only included for normal releases. The unconditional `--latest` should be removed from the command.

## Additional Requirements

- Add a comment explaining that the script runs right after the release commit is pushed (the timing context)
- Add a comment explaining the conventional commit regex format pattern, using angle-bracket placeholders to label each captured group (e.g., `<hash>`, `<type>`, etc.)
- Add a comment explaining that non-conventional commits go to the "Other" group
- The script must pass Node.js syntax validation
- Keep the existing `prereleaseFlag` logic unchanged

## File to Modify

- `scripts/create-github-release.mjs`
