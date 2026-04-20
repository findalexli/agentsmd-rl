# Fix Author Attribution in GitHub Release Changelog

The release changelog generator script (`scripts/create-github-release.mjs`) is
failing to attribute authors correctly for most changelog entries.

## Problem

When generating GitHub release notes, the `appendAuthors` function should add
author information (like `by @username`) to changelog entries. However, author
attribution is only appearing on "Updated dependencies" lines, not on actual
feature/fix entries.

Looking at the changelog entries:

- Actual changes use PR links: `- Fixed navigation ([#6891](url))`
- Dependency updates use commit hashes: `` - Updated dependencies [`9a4d924`](url) ``

The script only recognizes the commit hash format, so only dependency updates
get author attribution.

## Expected Behavior

All changelog entries with PR references should have author attribution, like:

```
- Fixed navigation ([#6891](url)) by @authorname
```

## Implementation Requirements

The fix must enable the script to:

1. **Resolve authors for PR references** — implement a function named
   `resolveAuthorForPR` that fetches author information for PR numbers found in
   changelog entries. The GitHub API endpoint for pull request data is
   `https://api.github.com/repos/TanStack/router/pulls/{prNumber}`.

2. **Cache PR author lookups** — use a cache variable named `prAuthorCache` to
   avoid duplicate API calls when resolving PR authors.

3. **Match PR reference patterns** — use a regex pattern `/\[#(\d+)\]/` to
   extract PR numbers from lines containing patterns like `([#6891](url))`.
   Store the match result in a variable named `prMatch`.

4. **Attempt PR resolution before commit hash resolution** — since changeset
   entries use PR links (not commit hashes) for actual changes, PR-based
   attribution should be tried first. Store the commit hash match result in a
   variable named `commitMatch`, and ensure `prMatch` is checked before
   `commitMatch` in the logic flow.

5. **Consistent author format** — append ` by @${username}` when a username
   is found, using the same format as commit hash resolution.

6. **Preserve non-list items** — lines not starting with `- ` (list items) must
   pass through unchanged. Use `startsWith('- ')` to check the prefix.

## Constraints

- The script must continue to pass ESLint and Prettier checks.
