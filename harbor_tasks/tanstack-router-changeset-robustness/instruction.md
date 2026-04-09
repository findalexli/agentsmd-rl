# Fix Changeset Publishing Robustness

The release script at `scripts/create-github-release.mjs` has several fragile patterns that need fixing to make the changeset publishing process more robust.

## What's Broken

1. **Fragile git range calculation**: The script uses `HEAD~1` assumptions to find the previous release commit. This breaks if the commit structure changes.

2. **Brittle non-conventional commit parsing**: The script uses nested `indexOf(' ')` calls with manual slicing to parse commits that don't follow conventional commit format. This is error-prone.

3. **Wrong release flags**: The script always passes `--latest` to `gh release create`, but prereleases should NOT be marked as latest on GitHub.

## Files to Modify

- `scripts/create-github-release.mjs` - The release script

## What You Need to Do

1. **Fix the git range calculation**: Instead of using `HEAD~1` assumptions, properly extract release commits by:
   - Getting all commits matching `ci: changeset release` into an array
   - Using `releaseLogs[0]` for current release and `releaseLogs[1]` for previous
   - Building the commit range from explicit commits rather than fragile relative references

2. **Fix non-conventional commit parsing**: Replace the brittle double `indexOf(' ')` approach with a cleaner `split(' ')` based parser that:
   - Splits the line by spaces
   - Takes parts[0] as hash, parts[1] as email
   - Joins parts[2..] as the subject

3. **Fix the release flags**: Only add `--latest` for normal releases, not prereleases:
   - Add a conditional `latestFlag` variable
   - Use `--latest` for regular releases, omit it for prereleases

## Testing Your Changes

The script should still have valid Node.js syntax (verify with `node --check`).

The changes should not affect the core router functionality - this is a CI/release script fix only.

## Hints

- Look for patterns like `HEAD~1`, `indexOf(' ')`, and `--latest` in the script
- Add comments explaining the git range logic - the script runs right after the release commit is pushed
- For non-conventional commits, consider what happens with merge commits or other unusual formats
