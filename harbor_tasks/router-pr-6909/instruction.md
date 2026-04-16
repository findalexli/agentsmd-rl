# Task: Improve GitHub Release Changelog Generation

The GitHub release changelog generation in `scripts/create-github-release.mjs` currently creates verbose, package-centric release notes that are difficult to scan. The changelog is organized by individual package names, making it hard to see what types of changes were made across the release.

## Problem

The current implementation:
1. Extracts changelog entries from each package's `CHANGELOG.md` file
2. Groups entries under `#### package-name` headings
3. Resolves authors by looking up commit hashes in git history using `resolveAuthorForCommit` function and `authorCache`
4. Uses `appendAuthors` function to process changelog lines

This approach results in release notes that are organized around package structure rather than the nature of the changes. Users want to quickly see "what features were added" or "what bugs were fixed" rather than wade through package-by-package listings.

## Goal

Refactor the changelog generation to use **conventional commits** with **semantic grouping**:

1. Parse the git log directly using conventional commit format (`type(scope): message`)
   - The script must use `git log` with `--pretty=format:"%h %ae %s"` to get commit hash, author email, and subject
   - The script must filter out merge commits using `--no-merges`
   - Skip release commits (`ci: changeset release`)

2. Group commits by their type (feat, fix, perf, refactor, docs, chore, test, ci)
   - The script must define a `typeOrder` array containing exactly these types in this priority order: `['feat', 'fix', 'perf', 'refactor', 'docs', 'chore', 'test', 'ci']`
   - The script must define a `typeLabels` object mapping each type to these exact human-readable headings:
     - `feat: 'Features'`
     - `fix: 'Fix'`
     - `perf: 'Performance'`
     - `refactor: 'Refactor'`
     - `docs: 'Documentation'`
     - `chore: 'Chore'`
     - `test: 'Tests'`
     - `ci: 'CI'`
   - The script must create a `groups` object and populate commits by type using `groups[type]`
   - Non-conventional commits must be grouped as `other`

3. Sort type sections by importance (features and fixes must appear before docs and chores)
   - The script must implement a `typeIndex` function that returns the index of a type in `typeOrder`
   - The script must sort types using `typeIndex(a) - typeIndex(b)`

4. Use `### ${label}` headings (e.g., `### Features`, `### Fix`) instead of package-based headings
   - The script must NOT use the old `#### ${pkg.name}` pattern

5. Continue to attribute commits to their PR authors where applicable
   - The script must keep the `resolveAuthorForPR` function
   - The script must keep `prAuthorCache` for caching PR author lookups
   - The script must remove the `resolveAuthorForCommit` function
   - The script must remove `authorCache` (the cache for commit-based lookups)
   - The script must remove the `appendAuthors` function and any calls to it

6. Stop reading from `CHANGELOG.md` files
   - The script must NOT call `fs.readFileSync(changelogPath)`

The result should be a cleaner, more scannable changelog that highlights the semantic nature of changes rather than the package structure.

## Files to Modify

- `scripts/create-github-release.mjs` - The main release script that generates changelog content

## Implementation Notes

- Parse conventional commits using a regex pattern like `/^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/` to extract type, scope, and message
- Store the regex match result in a variable named `conventionalMatch`
- The script runs after a changeset release commit is pushed
- PR author resolution via GitHub API for PR numbers must be preserved
