# Support Semver Breaking Changes in Release Script

The `scripts/create-github-release.mjs` script generates GitHub release notes from conventional commits. Currently, it doesn't recognize the breaking change marker (`!`) in conventional commit messages like `feat!: new API` or `fix(scope)!: critical fix`.

## Problem

When a commit message uses the `!` syntax to indicate a breaking change (e.g., `feat!: add breaking feature`), the script:
1. Doesn't capture the `!` marker in its regex
2. Doesn't have a dedicated "Breaking Changes" section in the release notes
3. Places breaking changes in their original type sections (Features, Fixes, etc.) instead of highlighting them

## Task

Modify `scripts/create-github-release.mjs` to properly handle breaking changes:

1. **Update the regex** to capture the `!` marker as a separate group
2. **Add `isBreaking` variable** that checks if the commit has the `!` marker
3. **Add 'breaking' to typeOrder** - should appear before 'feat'
4. **Add 'breaking' to typeLabels** - use "⚠️ Breaking Changes" as the label
5. **Update the bucket assignment** - if `isBreaking` is true, use 'breaking' as the bucket instead of the commit type
6. **Update the message group index** - when adding the `!` capture group, the message index shifts

## Files to Modify

- `scripts/create-github-release.mjs` - The release notes generation script

## Hints

- Look for the `conventionalMatch` regex pattern
- The current regex is: `/^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/`
- The new regex should capture `(!)?` before the colon
- When you add a capture group, subsequent group indices shift by 1
- Breaking changes should appear first in the release notes

## Testing

You can test your changes by checking that the script syntax is valid with `node --check scripts/create-github-release.mjs`.
