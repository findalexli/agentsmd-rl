# Breaking Changes Not Recognized in Release Notes

The GitHub release script (`scripts/create-github-release.mjs`) doesn't properly handle breaking changes in conventional commits.

## The Problem

When a commit uses the conventional commit format for breaking changes (with `!` before the colon), the release script fails to recognize it. For example:

- `feat!: new breaking feature` - should be grouped under "Breaking Changes"
- `fix(api)!: breaking API change` - should be grouped under "Breaking Changes"

Currently, these commits are either:
1. Not matched at all by the conventional commit parser
2. Grouped under their regular type (feat, fix, etc.) without any breaking change indication

## Expected Behavior

Breaking changes marked with `!` should:
1. Be recognized by the commit message parser (the regex assigned to `conventionalMatch` using `subject.match()`)
2. Be grouped separately under a "Breaking Changes" section
3. Appear at the top of the changelog (since breaking changes are most important)

## Implementation Requirements

The script uses these specific variable names and structures:

- **`typeOrder`**: An array that defines the order of sections in the changelog. It must include the type key `'breaking'` and it should be first in the array so breaking changes appear at the top.

- **`typeLabels`**: An object that maps type keys to their display labels. It must include an entry for the type key `breaking` with an appropriate label containing "Breaking" (e.g., "⚠️ Breaking Changes").

- **`isBreaking`**: Create a variable with this exact name to track whether a commit is a breaking change.

- **`bucket`**: Create a variable with this exact name to determine which section a commit belongs to. It should use the type key `"breaking"` for breaking changes.

- **Regex pattern**: The conventional commit regex must be updated to:
  - Include `(!)?` to optionally capture the `!` breaking marker in a group
  - Continue to match regular commits without `!`
  - Handle both scoped and unscoped commits with `!` (e.g., `feat!: message` and `feat(api)!: message`)
  - The pattern should produce captured groups where: group 1 is the type, group 2 is the optional scope, group 3 is the optional `!` marker, and group 4 is the message

- **Message extraction**: After modifying the regex, ensure commit messages are extracted from the correct capture group. The message should come after the type (and optional scope) and the optional `!` marker.

## Files to Modify

- `scripts/create-github-release.mjs` - The release script that parses commits and generates changelog

Look at how conventional commits are parsed (the regex pattern), how the `typeOrder` array controls section ordering, how `typeLabels` provides section titles, and how commits are grouped into buckets by type.
