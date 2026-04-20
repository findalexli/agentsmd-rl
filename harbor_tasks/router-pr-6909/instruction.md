# Task: Improve GitHub Release Changelog Generation

The GitHub release changelog generation in `scripts/create-github-release.mjs` currently creates verbose, package-centric release notes that are difficult to scan. The changelog is organized by individual package names, making it hard to see what types of changes were made across the release.

## Problem

The current implementation has these issues:

1. **Reads CHANGELOG.md files**: The script extracts changelog entries from each package's `CHANGELOG.md` file using `fs.readFileSync(changelogPath)`. This approach should not be used.

2. **Package-based grouping**: Groups entries under `#### package-name` headings, which focuses on package structure rather than the nature of changes.

3. **Commit-based author resolution**: Uses `resolveAuthorForCommit` function and `authorCache` to look up commit authors by hash. This approach should be removed.

4. **appendAuthors processing**: Uses `appendAuthors` function to process changelog lines. This function and all calls to it should be removed.

5. **Merge commits included**: Merge commits are not being filtered out from the git history.

6. **No conventional commit parsing**: The script doesn't parse conventional commit format (`type(scope): message`) to categorize changes.

## Goal

Refactor the changelog generation to use **conventional commits** with **semantic grouping**:

1. **Parse git log directly**: Use `git log` with `--pretty=format:"%h %ae %s"` to get commit hash, author email, and subject between releases.

2. **Filter merge commits**: Exclude merge commits using `--no-merges`.

3. **Parse conventional commits**: Extract the commit type (feat, fix, perf, refactor, docs, chore, test, ci) and scope from commit messages following the pattern `type(scope): message`.

4. **Group by type**: Group commits by their conventional commit type:
   - feat → "Features"
   - fix → "Fix"
   - perf → "Performance"
   - refactor → "Refactor"
   - docs → "Documentation"
   - chore → "Chore"
   - test → "Tests"
   - ci → "CI"
   - Non-conventional commits go to an "other" category

5. **Sort by importance**: Sort the type sections so that feat and fix appear before docs, chore, test, and ci.

6. **Generate markdown with type headings**: Use `### ${label}` headings (e.g., `### Features`, `### Fix`) instead of `#### ${pkg.name}` package headings.

7. **Skip release commits**: Filter out commits with message starting with `ci: changeset release`.

8. **Preserve PR author resolution**: Keep `resolveAuthorForPR` function and `prAuthorCache` for looking up PR authors via GitHub API.

## Files to Modify

- `scripts/create-github-release.mjs` - The main release script that generates changelog content

## Implementation Notes

- The script runs after a changeset release commit is pushed
- For commits with PR references like `(#1234)`, look up the author using the PR number
- For commits without PR references, use the commit author email
- Skip merge commits and the automated release commit itself
- The changelog should list commits with their scope prefix (if any), message, commit hash, and author attribution
