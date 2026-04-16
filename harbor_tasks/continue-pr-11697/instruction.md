# Discover Review Files in `.continue/checks/`

When running `cn review`, the CLI should discover local review files from both `.continue/agents/` and `.continue/checks/` directories. Currently, review files placed in `.continue/checks/` are not discovered — only files in `.continue/agents/` are found.

## The Problem

The local review discovery logic currently only scans one directory. This means:

- Users following the Continue README and quickstart docs (which direct users to create files in `.continue/checks/`) get zero local reviews discovered
- The CLI onboarding path is broken for users who follow the standard documentation

## Requirements

1. **Scan both directories**: The local review discovery must scan both `.continue/agents/` and `.continue/checks/` directories, in that order (agents first, then checks).

2. **Deduplicate with precedence**: When the same filename exists in both directories, use a `Set` to track `seen` filenames, with the agents directory taking precedence over checks (first occurrence wins).

3. **Update documentation**: The source code comments/docstrings should mention both `agents` and `checks` directories.

4. **Add unit tests**: Create a test file at `extensions/cli/src/commands/review/resolveReviews.test.ts` with vitest tests that verify:
   - Files are discovered from `.continue/agents/`
   - Files are discovered from `.continue/checks/`
   - Files from both directories are deduplicated correctly with agents taking precedence
   - Empty array returned when neither directory exists
   - Errors are handled gracefully

## What to Fix

Find the code in the CLI that resolves local review files (currently only reading from one directory) and modify it to:
- Scan both `.continue/agents/` and `.continue/checks/` directories
- Use a Set-based deduplication approach with a `seen` tracker for filenames
- Ensure agents directory takes precedence when duplicate filenames exist
- Update relevant doc comments to mention both directories
- Create the test file at `extensions/cli/src/commands/review/resolveReviews.test.ts`
