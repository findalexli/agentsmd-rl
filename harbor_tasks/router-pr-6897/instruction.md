# Improve GitHub Release Changelog Script

## Problem

The `scripts/create-github-release.mjs` script generates GitHub release notes for this monorepo, but it has several issues with how it constructs the changelog:

1. **Parses raw git commits instead of using changesets**: The script currently extracts commits between releases using `git log` and groups them by conventional commit type (Feat, Fix, Refactor, etc.). However, this repo uses [changesets](https://github.com/changesets/changesets) which already generates well-formatted `CHANGELOG.md` files in each package directory. The script should leverage these existing changelog files instead of re-parsing commits.

2. **Lists all packages regardless of changes**: The release notes include every non-private package in the repo, even ones that weren't actually changed in the release. Only packages with actual version bumps should be listed.

3. **Missing author attribution on changelog entries**: The changeset-generated `CHANGELOG.md` files include commit hash links (like `` [`9a4d924`](url) ``) but don't show who made each change. It would be helpful to append author attribution (e.g., "by @username") to entries that contain commit hashes.

## Expected Behavior

After the fix:

1. The script should read changelog entries from each package's `CHANGELOG.md` file (located at `packages/<pkg>/CHANGELOG.md`), extracting the section that corresponds to the current version being released. Use a `changelogPath` variable to hold the path to each `CHANGELOG.md` file, and use `readFileSync` to read the file content. Parse the version section by locating the `## <version>` header (store this header string in a `versionHeader` variable) and extracting content until the next `## ` section or end of file.

2. Only packages that were actually bumped (where the current version differs from the previous release's version) should appear in the release notes. Track bumped packages in a `bumpedPackages` variable. The version comparison must use the expression `prevPkg.version !== currentPkg.version` to detect version changes between the previous release commit and the current workspace.

3. Changelog entries containing commit hash links should have author attribution appended. Use a regex pattern matching hexadecimal characters `[a-f0-9]` to find commit hashes in lines. Match commit hash links using a `commitMatch` regex variable. Resolve commit hashes to author strings using an `authorCache` object to cache results and an async function `resolveAuthorForCommit` that maps hash → " by @username" string. Add author attribution to changelog lines using an async function `appendAuthors` that processes lines containing commit hash links.

4. The output format should organize changelog entries by package name using `#### ${pkg.name}` as the section header format (four hash marks followed by the package name in braces), rather than organizing by commit type.

5. When there are no changelog entries to report, use the message `- No changelog entries` (with both words capitalized) instead of the previous `- None` fallback.

## Implementation Requirements

The script must include:
- An async function named `resolveAuthorForCommit` that takes a commit hash argument and returns the author attribution string (e.g., `" by @username"`)
- An async function named `appendAuthors` that processes changelog content and appends author attribution to lines containing commit hash links
- A variable named `authorCache` to cache resolved author results by commit hash
- A variable named `commitMatch` for the regex that matches commit hash links
- A variable named `bumpedPackages` to track packages with version changes
- A variable named `changelogPath` to hold the path to each `CHANGELOG.md` file
- A variable named `versionHeader` storing the version header string (e.g., `"## <version>"`)
- Version comparison using `prevPkg.version !== currentPkg.version`
- Package section headers using `#### ${pkg.name}` format

## Files to Modify

- `scripts/create-github-release.mjs`

## Notes

- The script runs after a "ci: changeset release" commit is pushed
- It uses `git show <commit>:path` to read file contents from previous commits
- The GitHub API is used to resolve commit author emails to GitHub usernames
- Changesets writes version headers as `## <version>` in CHANGELOG.md files
- The script should only use ESM imports (`fs`, `path`, `execSync`, `globSync`)
- The GitHub token is available via `GH_TOKEN` or `GITHUB_TOKEN` environment variables
