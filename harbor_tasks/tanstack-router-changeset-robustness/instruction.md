# Fix Changeset Publishing Robustness

The release script at `scripts/create-github-release.mjs` has three robustness issues that need fixing to make the changeset publishing process more reliable.

## Issues to Fix

### 1. Fragile Git Range Calculation

The script currently assumes `HEAD~1` to find the previous release commit. When it runs `git log` with `HEAD~1`, it only looks back one commit, which breaks if the commit history doesn't match this assumption.

The fix should:
- Query all commits matching `ci: changeset release` from git log (not just the most recent one)
- Parse the output into an array of commit hashes by splitting on newlines and filtering out falsy/empty values
- Use the first array element as the current release commit and the second as the previous release commit
- Build the git log range from these explicit commit references rather than relative ones like `HEAD~1`
- Include a fallback for when no previous release commit exists
- Add a comment explaining the context — that this script runs right after the release commit is pushed, so HEAD is the release commit

### 2. Brittle Non-Convention Commit Parsing

For commits that don't follow the conventional commit format, the script uses nested `indexOf(' ')` calls with manual slicing to extract the hash, email, and subject. This is fragile and error-prone.

The fix should:
- Replace the double `indexOf` approach with a cleaner split-based parser
- Split each non-conventional commit line on spaces to get individual parts
- The first part is the hash, the second is the email, and the remaining parts re-joined with spaces form the subject
- Remove the old brittle approach entirely
- Add a comment about handling non-conventional commits (e.g., merge commits)

### 3. Incorrect Release Flags for Prereleases

The script always passes `--latest` to `gh release create`, but prerelease versions should NOT be marked as the latest release on GitHub.

The fix should:
- Conditionally include `--latest` only for non-prerelease releases
- Define a variable for the latest flag, set to `--latest` for regular releases and empty for prereleases, using a ternary based on the existing `isPrerelease` variable
- Use this flag variable in the `gh release create` command template

## File to Modify

`scripts/create-github-release.mjs`

## Validation

After making changes, verify:
- `node --check scripts/create-github-release.mjs` passes (valid syntax)
- `npx prettier --check scripts/create-github-release.mjs` passes
- `npx eslint scripts/create-github-release.mjs` passes
