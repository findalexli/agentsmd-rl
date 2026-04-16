# Task: Improve GitHub Release Changelog Generation

## Problem Description

The `scripts/create-github-release.mjs` script currently generates release notes by parsing raw git commits and grouping them by conventional commit type (Feat, Fix, Refactor, etc.). This approach has several problems:

1. **No author attribution**: The changelog doesn't show who made each change
2. **Shows all packages**: Lists every package in the workspace, even those without changes
3. **Manual commit parsing**: Groups commits manually instead of using the rich changelog data from changesets

## What Needs to Change

Refactor the script to fix the above problems:

1. **Extract from CHANGELOG.md files**: Instead of parsing git commits, read the changeset-generated `CHANGELOG.md` files from each package's directory and extract entries under the current version header.

2. **Add author attribution**: Changelog entries currently show commit hash references like `[\`abc1234\`](url)` with no author name. Resolve the GitHub username from the commit author email and append it to the line as " by @username".

3. **Only show bumped packages**: Compare package.json versions between the current release and the previous release commit. Only include packages whose version actually changed in the release notes.

4. **Handle edge cases**:
   - New packages that didn't exist in the previous release should still appear in the changelog
   - Gracefully handle cases where username resolution fails

## Old Patterns to Remove

The script currently has these patterns that must be removed:

- Git log parsing with format string `--pretty=format:"%h %ae %s"`
- Conventional commit grouping with `const groups = {}`, `const typeOrder = [`, and `for (const type of sortedTypes)`
- Type-related labels: `'Feat'`, `'Fix'`, `'Refactor'`, `typeIndex`, `sortedTypes`

## Required Behaviors

### Author Resolution

The script needs an async function that takes a commit hash and returns the GitHub username of the commit's author. It should:
1. Run `git log -1 --format=%ae <hash>` to get the author email
2. Resolve that email to a GitHub username
3. Return the username string

### Content Processing

The script needs an async function that processes changelog text content and appends author information to lines that contain commit hash references. For each line matching the pattern `[\`hash\`](url)`, resolve the hash to a username and append ` by @username`.

### Version Comparison

Build a list of packages whose versions changed between releases:
- Compare `prevPkg.version` against `currentPkg.version`
- If they differ, the package should be included
- If the package didn't exist in the previous release (git show fails), include it anyway with `prevVersion: null`

### Output Format

For each included package, output a section with:
- A header using the package name
- The version number
- The changelog entries for that version (with author attribution if available)
- Sorted alphabetically by package name

## Context

- The script runs right after the "ci: changeset release" commit is pushed
- Changeset-generated changelogs have entries under "## \<version>" headers
- Commit hashes in changelog lines appear as: `[\`hash\`](url)`