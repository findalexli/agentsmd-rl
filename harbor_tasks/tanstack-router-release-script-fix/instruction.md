# Fix Release Script Robustness Issues

The `scripts/create-github-release.mjs` script has several fragility issues that need to be fixed to make the release process more robust.

## Issues to Fix

### 1. Fragile Git Commit Range Detection
The current script uses `HEAD~1` assumptions to find the previous release commit, which is error-prone. The script should:
- Get all release commits by grepping for "ci: changeset release"
- Parse the results as an array (split by newline, filter empty strings)
- Use `releaseLogs[0]` as the current release (HEAD) and `releaseLogs[1]` as the previous release
- Calculate `rangeFrom` using `previousRelease` if available, falling back to `${currentRelease}~1`
- Use `${rangeFrom}..${currentRelease}` for the git log range instead of `..HEAD~1`

### 2. Brittle Non-Conventional Commit Parsing
The current code uses double `indexOf(' ')` to parse non-conventional commits, which is fragile. Replace this with:
- Use `line.split(' ')` to split the line into parts
- Extract `hash` from `parts[0]`, `email` from `parts[1]`, and `subject` from `parts.slice(2).join(' ')`

### 3. Incorrect --latest Flag Handling
The `--latest` flag should only be set for normal (non-prerelease) releases. Currently it's always passed:
- Create a `latestFlag` variable that is empty string for prereleases and `' --latest'` for normal releases
- Include `${latestFlag}` in the `gh release create` command
- Remove the unconditional `--latest` from the command

## Context

The script runs immediately after the "ci: changeset release" commit is pushed, so HEAD is always the release commit. The goal is to get commits between the previous release and the current one, excluding both release commits themselves.

The non-conventional commit parsing handles merge commits and other entries that don't follow the conventional commit format of "type(scope): subject".

## Files to Modify

- `scripts/create-github-release.mjs` - Main release script

## Hints

- Look for the `lastReleaseHash` variable - this is where the fragile `HEAD~1` logic lives
- Look for `indexOf(' ')` usage - this is the brittle parsing that needs replacing
- Look for the `gh release create` command - this is where `--latest` handling needs fixing
- Add helpful comments explaining the release commit timing and commit format patterns
