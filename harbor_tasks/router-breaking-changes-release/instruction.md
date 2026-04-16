# Support Semver Breaking Changes in Release Notes

The release notes generation script (`scripts/create-github-release.mjs`) currently doesn't properly handle breaking changes marked with the exclamation mark (!) in conventional commit messages.

## Problem

When a commit follows the conventional commit format with a breaking change indicator like:
- `feat!: add new breaking feature`
- `fix!: fix critical breaking bug`
- `feat(scope)!: scoped breaking change`

The script fails to recognize these as breaking changes. Instead, commits with `!` in the message are not properly categorized.

## Expected Behavior

1. The conventional commit regex should be updated to parse the optional `!` marker before the colon
2. Breaking changes (commits with `!`) should be categorized in a dedicated "⚠️ Breaking Changes" section
3. The breaking changes section should appear first in the release notes, before features and fixes
4. Non-breaking commits should continue to be categorized in their respective sections (feat, fix, etc.)

## Files to Modify

- `scripts/create-github-release.mjs` - The release notes generation script

Look for the conventional commit parsing logic and the type ordering/type labels arrays. The regex for parsing needs to handle the `!` marker, and there should be logic to bucket breaking changes separately from regular changes.

## Testing

The parsing logic can be tested by simulating commit messages with and without the `!` marker. Breaking changes should be routed to a 'breaking' bucket while regular changes go to their type-specific buckets.
